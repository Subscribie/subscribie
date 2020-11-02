from subscribie.models import PaymentProvider
from flask import current_app


def get_stripe_secret_key():
    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return current_app.config.get("STRIPE_LIVE_SECRET_KEY", None)
    else:
        return current_app.config.get("STRIPE_TEST_SECRET_KEY", None)


def get_stripe_publishable_key():
    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return current_app.config.get("STRIPE_LIVE_PUBLISHABLE_KEY", None)
    else:
        return current_app.config.get("STRIPE_TEST_PUBLISHABLE_KEY", None)
