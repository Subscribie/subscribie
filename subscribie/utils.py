from flask import current_app, request, g
import stripe
from subscribie import database


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
    account = stripe.Account.create(
        type="express",
        email=g.user.email,
        default_currency="gbp",
        business_profile={"url": request.host_url, "name": company.name},
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
        print(e)
        raise
    except stripe.error.InvalidRequestError as e:
        print(e)
        raise
    except Exception as e:
        print(e)
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


def modify_stripe_account_capability(account_id):
    """Request (again) card_payments capability after kyc onboarding
    is complete"""
    stripe.Account.modify_capability(account_id, "card_payments", requested=True)


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
