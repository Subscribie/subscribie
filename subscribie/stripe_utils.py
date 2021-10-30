from subscribie import database
from flask import current_app, request, g, session
import stripe

from flask_saas import StripeBusinessProfile

from subscribie import database
import logging

log = logging.getLogger(__name__)


def get_stripe_secret_key():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return current_app.config.get("STRIPE_LIVE_SECRET_KEY", None)
    else:
        return current_app.config.get("STRIPE_TEST_SECRET_KEY", None)


def get_stripe_publishable_key():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return current_app.config.get("STRIPE_LIVE_PUBLISHABLE_KEY", None)
    else:
        return current_app.config.get("STRIPE_TEST_PUBLISHABLE_KEY", None)


def create_stripe_connect_account(company):
    stripe.api_key = get_stripe_secret_key()
    if "127.0.0.1" in request.host_url:
        url = "blackhole-1.iana.org"
    else:
        url = request.host_url

    account = stripe.Account.create(
        type="express",
        email=g.user.email,
        default_currency="gbp",
        business_profile={"url": url, "name": company.name},
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
    )

    return account


def get_stripe_connect_account():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    stripe.api_key = get_stripe_secret_key()

    if payment_provider.stripe_livemode:
        account_id = payment_provider.stripe_live_connect_account_id
    else:
        account_id = payment_provider.stripe_test_connect_account_id

    if account_id is None or account_id == "":
        return None

    try:
        account = stripe.Account.retrieve(account_id)
    except stripe.error.PermissionError as e:
        log.error(f"Stripe PermissionError {e}")
        raise
    except stripe.error.InvalidRequestError as e:
        log.error(f"Stripe InvalidRequestError {e}")
        raise
    except Exception as e:
        log.info(f"Exception getting Stripe connect account {e}")
        account = None

    return account


def get_stripe_connect_account_id():
    """Get stripe connect account id locally without querying Stripe api"""
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        account_id = payment_provider.stripe_live_connect_account_id
    else:
        account_id = payment_provider.stripe_test_connect_account_id

    return account_id


def set_stripe_connect_account_id(account_id: str) -> str:
    """Set stripe connect account id locally without querying Stripe api"""
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        payment_provider.stripe_live_connect_account_id = account_id
    else:
        payment_provider.stripe_test_connect_account_id = account_id

    database.session.commit()
    session["account_id"] = account_id

    return account_id


def stripe_connect_active():
    stripe.api_key = get_stripe_secret_key()
    connect_account_id = get_stripe_connect_account_id()
    if stripe.api_key is None or stripe.api_key == "":
        return False
    if connect_account_id is None:
        return False
    try:
        stripe.Balance.retrieve(stripe_account=connect_account_id)
        return True
    except Exception as e:
        log.info(f"Could not get Stripe balance {e}")
        return False


def format_to_stripe_interval(plan: str):
    """Format plan.interval_unit to Stripe accepted interval
    https://stripe.com/docs/api/checkout/sessions/create#create_checkout_session-line_items-price_data-recurring-interval
    """
    if plan == "daily":
        plan = "day"
    elif plan == "weekly":
        plan = "week"
    elif plan == "monthly":
        plan = "month"
    elif plan == "yearly":
        plan = "year"
    else:
        return ""
    return plan


def create_stripe_tax_rate():
    from .models import PaymentProvider
    from subscribie.models import TaxRate

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        livemode = True
    else:
        livemode = False

    # If there's no tax rate for current live mode create and save one:
    if TaxRate.query.filter_by(stripe_livemode=livemode).first() is None:
        stripe.api_key = get_stripe_secret_key()
        tax_rate = stripe.TaxRate.create(
            stripe_account=get_stripe_connect_account_id(),
            display_name="VAT",
            description="VAT UK",
            jurisdiction="GB",
            percentage=20,
            inclusive=False,
        )
        # Save tax_rate id and livemode to db
        newTaxRate = TaxRate()
        newTaxRate.stripe_livemode = tax_rate.livemode
        newTaxRate.stripe_tax_rate_id = tax_rate.id
        database.session.add(newTaxRate)
        database.session.commit()

    return True


def get_stripe_livemode():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return True
    return False


def set_stripe_livemode(livemode: int) -> bool:
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    payment_provider.stripe_livemode = livemode
    database.session.commit()
    return bool(livemode)


def get_stripe_connect_completed_status() -> bool:
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    return payment_provider.stripe_active


def set_stripe_connect_completed_status(status: bool) -> bool:
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    payment_provider.stripe_active = status
    database.session.commit()


def get_stripe_business_profile():
    """
    Return dict valid for Stripe acounnt business_profile
    See:
    https://stripe.com/docs/api/accounts/object#account_object-business_profile
    """
    from .models import Company

    company = Company.query.first()

    return {"name": company.name, "email": g.user.email}
