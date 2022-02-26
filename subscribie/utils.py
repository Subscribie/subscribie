from flask import current_app, request, g
import stripe
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


def get_stripe_failed_subscription_invoices():
    """Return Stripe invoices which have failed, and
    were generated via a Stripe Subscription.

    An Stripe Invoice may reach this stage when

    - All automatic payment rety attempts have failed
    - Failed Stripe Invoices have a null value for "next_payment_attempt"
    - Failed Stripe Invoices payment `attempt_count` is *often*
        equal to the max retry attempts + 1
        (first attempt + max number of retries).
    - Note `attempt_count` could be less than max number of retries if the
        connected account goes away, gets disconnected, other reasons),
        do not rely on it as a metric for failed.

    NOTE: Stripe has no formal definition of a "failed"
         status for an Invoice (even though in the
         Stripe UI the word 'failed' is displayed to the
         user). The official Stripe Subscription statuses
         are documented here:
         https://stripe.com/docs/billing/subscriptions/overview#subscription-statuses

         In the context of Subscribie: A failed invoice
         is an Invoice for which no further automatic charge will
         be attempted for *that* Invoice.

         "No further automatic charge" is *very* important
         given if a Shop owner decides to collect money owed
         outside of the platform, it is beneficial for the
         shop owner to know that no further automatic charge will
         be taken for *that* invoice.

         Remember, however, that if
         a Subscription is still active, then *new* invoices,
         and therefore new charge attempts will be generated for the
         active Subscription as expected.


    NOTE: Stripe Invoices which are generated via a
    Stripe Subscription are generated automatically
    by Stripe and therefore have different properties
    to manually created invoices, most notably the
    'collection_method' field'.
    See https://stripe.com/docs/billing/subscriptions/overview
    """
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    invoices = stripe.Invoice.list(
        collection_method="charge_automatically",
        stripe_account=stripe_connect_account_id,
        limit=100,
    )

    failedInvoices = []
    for invoice in invoices.auto_paging_iter():
        if (
            invoice.status == "open"
            and invoice.next_payment_attempt is None
            and invoice.status != "paid"
        ):
            # Means invoice is no longer being auto collected,
            failedInvoices.append(invoice)
    return failedInvoices


def get_stripe_void_subscription_invoices():
    """Return Stripe invoices which are in Stripe Invoice state "void"
    See also get_stripe_failed_subscription_invoices for detail.

    NOTES:

    A 'void' Stripe Subscription can be due to many reasons
    here are some possible reasons:

    - a Subscription expired before payment was taken
    - Read get_stripe_failed_subscription_invoices method doc block
    - See also https://stripe.com/docs/billing/subscriptions/overview#subscription-statuses # noqa
    """
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    invoices = stripe.Invoice.list(
        collection_method="charge_automatically",
        stripe_account=stripe_connect_account_id,
        limit=100,
    )

    voidInvoices = []
    for invoice in invoices.auto_paging_iter():
        if (
            invoice.status == "void"
            and invoice.next_payment_attempt is None
            and invoice.status != "paid"
        ):
            voidInvoices.append(invoice)
    return voidInvoices
