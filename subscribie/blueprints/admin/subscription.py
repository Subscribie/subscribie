from subscribie.models import Subscription
from subscribie.database import database
from subscribie.stripe_utils import (
    get_stripe_secret_key,
    get_stripe_connect_account,
    stripe_connect_active,
)
import stripe
import logging


def update_stripe_subscription_statuses():
    """Update Stripe subscriptions with their current status
    by querying Stripe api"""
    stripe.api_key = get_stripe_secret_key()
    connect_account = get_stripe_connect_account()
    if stripe.api_key is None:
        logging.error("Stripe api key not set refusing to update subscription statuses")
    if connect_account is None:
        logging.error(
            "Stripe connect account not set. Refusing to update subscription statuses"
        )
    if stripe_connect_active():
        for subscription in Subscription.query.all():
            try:
                stripeSubscription = stripe.Subscription.retrieve(
                    stripe_account=connect_account.id,
                    id=subscription.stripe_subscription_id,
                )
                subscription.stripe_status = stripeSubscription.status
                database.session.commit()
            except Exception as e:
                logging.warning(f"Could not update stripe subscription status: {e}")
    else:
        logging(
            "Refusing to update subscription status since Stripe connect is not active"
        )
