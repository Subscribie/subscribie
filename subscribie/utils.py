from subscribie.models import PaymentProvider
from flask import current_app
import stripe


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


def get_stripe_connect_account():
    payment_provider = PaymentProvider.query.first()
    stripe.api_key = get_stripe_secret_key()

    if payment_provider.stripe_livemode:
        account_id = payment_provider.stripe_live_connect_account_id
    else:
        account_id = payment_provider.stripe_test_connect_account_id

    if account_id is None or account_id == "":
        raise NameError("account_id is not set")

    try:
        account = stripe.Account.retrieve(account_id)
    except stripe.error.PermissionError as e:
        print(e)
        raise
    except stripe.error.InvalidRequestError as e:
        print(e)
        raise
    except Exception as e:
        print(e)
        account = None

    return account
