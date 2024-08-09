from subscribie.models import Subscription
from subscribie.database import database
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account,
    get_stripe_connect_account_id,
    stripe_connect_active,
)
from subscribie.tasks import background_task
from subscribie.blueprints.checkout import create_subscription
import stripe
import logging


log = logging.getLogger(__name__)


def update_stripe_subscription_status(subscription_uuid):
    """Fetch the status of a single Stripe subscription
    by querying the status of the subscription object at
    Stripe.
    """
    stripe.api_key = get_stripe_secret_key()
    connect_account_id = get_stripe_connect_account_id()
    if stripe.api_key is None:
        msg = "Stripe must be connected first"
        log.warning(msg)
        return msg, 500

    if stripe_connect_active() is False:
        msg = "Stripe connect must be connected."
        log.ingo(msg)
        return msg, 500

    subscription = (
        database.session.query(Subscription)
        .where(Subscription.uuid == subscription_uuid)
        .first()
    )
    if subscription:
        # Get associated stripe subscription object & update status
        try:
            stripeSubscription = stripe.Subscription.retrieve(
                subscription.stripe_subscription_id, stripe_account=connect_account_id
            )
            log.debug(
                f"setting Subscribie subscription {subscription.uuid} status to: {stripeSubscription.status} for Stripe subscription: {stripeSubscription.id}"  # noqa: E501
            )

            subscription.stripe_status = stripeSubscription.status
            if stripeSubscription.created is not None:
                subscription.stripe_start_date = stripeSubscription.created

            # Update stripeSubscription.ended_at if stripe subscription has ended  # noqa: E501
            if stripeSubscription.ended_at is not None:
                subscription.stripe_ended_at = stripeSubscription.ended_at
            log.info(subscription.stripe_status)
            log.info(subscription.stripe_subscription_id)
            database.session.commit()
        except Exception as e:
            log.error("Failed updating individual subscription status. {e}")
            return "Failed updating individual subscription status.", 500


@background_task
def update_stripe_subscription_statuses(app):
    """Update Stripe subscriptions with their current status
    by querying Stripe api.

    A subscription status can include: incomplete, incomplete_expired,
    trialing, active, past_due, canceled, unpaid, or paused.

    If a subscription object exists in Stripe, but does
    not exist in Subscribie*, it's metadata is pulled from
    Stripe and Subscribie's database is brought up to date.

    *In the majority case, a Subscribie Subscription object
    is created upon Stripe Subscription creation right after
    a Stripe `checkout.session.completed` event is processed by
    the /stripe_webhook endpoint, however, if webhook fails all retrys
    this task also recovers from those webhook delivery failures (and
    can be triggered manually via 'Refresh Subscriptions' on the
    admin subscribers page.

    See also:
    - https://docs.stripe.com/api/subscriptions/object#subscription_object-status

    :param: app (required) note app is automatically injected by @background_task decorator # noqa: E501
    """
    with app.app_context():
        stripe.api_key = get_stripe_secret_key()
        connect_account = get_stripe_connect_account()
        if stripe.api_key is None:
            log.warning(
                "Stripe api key not set refusing to update subscription statuses"
            )  # noqa: E501
        if connect_account is None:
            log.warning(
                "Stripe connect account not set. Refusing to update subscription statuses"  # noqa: E501
            )
        count = 0
        if stripe_connect_active():
            try:
                # See https://stripe.com/docs/api/subscriptions/list#list_subscriptions-status # noqa: E501
                stripeSubscriptions = stripe.Subscription.list(
                    stripe_account=connect_account.id, status="all", limit=100
                )
                for stripeSubscription in stripeSubscriptions.auto_paging_iter():
                    count += 1
                    print(f"Subscription refresh tally: {count}")
                    log.debug(
                        f"processing subscription status for Stripe subscription: {stripeSubscription.id}"  # noqa: E501
                    )

                    subscription = (
                        database.session.query(Subscription)
                        .where(
                            Subscription.stripe_subscription_id == stripeSubscription.id
                        )
                        .first()
                    )
                    if subscription:
                        log.debug(
                            f"setting Subscribie subscription {subscription.uuid} status to: {stripeSubscription.status} for Stripe subscription: {stripeSubscription.id}"  # noqa: E501
                        )

                        subscription.stripe_status = stripeSubscription.status
                        # Update stripeSubscription.ended_at if stripe subscription has ended  # noqa: E501
                        if stripeSubscription.ended_at is not None:
                            subscription.stripe_ended_at = stripeSubscription.ended_at
                        if stripeSubscription.created is not None:
                            subscription.stripe_start_date = stripeSubscription.created
                        log.info(subscription.stripe_status)
                        log.info(subscription.stripe_subscription_id)
                        database.session.commit()
                    else:
                        log.warning(
                            f"subscription {stripeSubscription.id} is in stripe but not in the subscribie database"  # noqa: E501
                        )
                        log.warning(
                            "Trying to recover missed subscription creation from Stripe"
                        )
                        email = stripe.Customer.retrieve(
                            stripeSubscription.customer,
                            stripe_account=connect_account.id,
                        ).email
                        currency = stripeSubscription.currency.upper()
                        metadata = stripeSubscription.metadata
                        package = metadata.package
                        chosen_option_ids = metadata.chosen_option_ids
                        subscribie_checkout_session_id = (
                            metadata.subscribie_checkout_session_id
                        )
                        stripe_subscription_id = stripeSubscription.id
                        create_subscription(
                            currency=currency,
                            email=email,
                            package=package,
                            chosen_option_ids=chosen_option_ids,
                            subscribie_checkout_session_id=subscribie_checkout_session_id,  # noqa: E501
                            stripe_subscription_id=stripe_subscription_id,
                        )
            except Exception as e:
                log.warning(f"Could not update stripe subscription status: {e}")
        else:
            log.warning(
                "Refusing to update subscription status since Stripe connect is not active"  # noqa: E501
            )
