from subscribie.models import Subscription
from subscribie.database import database
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account,
    stripe_connect_active,
)
from subscribie.tasks import background_task
import stripe
import logging


log = logging.getLogger(__name__)


@background_task
def update_stripe_subscription_statuses(app):
    """Update Stripe subscriptions with their current status
    by querying Stripe api

    :param: app (required) note app is automatically injected by @background_task decorator # noqa: E501
    """
    with app.app_context():
        stripe.api_key = get_stripe_secret_key()
        connect_account = get_stripe_connect_account()
        if stripe.api_key is None:
            log.error("Stripe api key not set refusing to update subscription statuses")
        if connect_account is None:
            log.error(
                "Stripe connect account not set. Refusing to update subscription statuses"  # noqa: E501
            )
        if stripe_connect_active():
            try:
                # See https://stripe.com/docs/api/subscriptions/list#list_subscriptions-status # noqa: E501
                stripeSubscriptions = stripe.Subscription.list(
                    stripe_account=connect_account.id, status="all", limit=100
                )
                for stripeSubscription in stripeSubscriptions.auto_paging_iter():
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
                        log.info(subscription.stripe_status)
                        log.info(subscription.stripe_subscription_id)
                        database.session.commit()
                    else:
                        log.warning(
                            "subscription is in stripe but not in the subscribie database"  # noqa: E501
                        )
            except Exception as e:
                log.warning(f"Could not update stripe subscription status: {e}")
        else:
            log.warning(
                "Refusing to update subscription status since Stripe connect is not active"  # noqa: E501
            )
