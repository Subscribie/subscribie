from flask import request, g, session, url_for
import stripe
from subscribie import settings, database
from currency_symbols import CurrencySymbols
import logging
from subscribie.tasks import background_task
from datetime import datetime, timedelta
import requests

log = logging.getLogger(__name__)

COUNTRY_CODE_TO_CURRENCY_CODE = {
    "US": "USD",
    "GB": "GBP",
    "AT": "EUR",
    "BE": "EUR",
    "CY": "EUR",
    "EE": "EUR",
    "FI": "EUR",
    "FR": "EUR",
    "DE": "EUR",
    "GR": "EUR",
    "IE": "EUR",
    "IT": "EUR",
    "LV": "EUR",
    "LT": "EUR",
    "LU": "EUR",
    "MT": "EUR",
    "NL": "EUR",
    "PT": "EUR",
    "SK": "EUR",
    "SI": "EUR",
    "ES": "EUR",
    "AU": "AUD",
}


def get_geo_currency_code():
    """If geo currency is enabled,
    Return currency code based on current detected (or selected)
    country code, otherwise, return the shops default currency code.
    """
    from subscribie.models import Setting

    settings = Setting.query.first()
    geo_currency_enabled = settings.geo_currency_enabled
    if geo_currency_enabled is True:
        country_code = get_geo_country_code()
        # Get currency code from COUNTRY_CODE_TO_CURRENCY_CODE mapping
        try:
            currency_code = COUNTRY_CODE_TO_CURRENCY_CODE[country_code]
        except KeyError as e:
            log.info(
                f"Could not map country_code {country_code} to a currency code. {e}"
            )
            currency_code = get_shop_default_currency_code()
        log.info(f"get_geo_currency_code returned currency_code: {currency_code}")
    else:
        log.info(
            f"geo_currency_enabled is {geo_currency_enabled} so returning shops default currency code"  # noqa: E501
        )
        currency_code = get_shop_default_currency_code()
        log.info(f"Default currency code returned: {currency_code}")
    return currency_code


def get_shop_default_country_code():
    """
    Returns shops default country code.
    """
    from subscribie.models import Setting

    settings = Setting.query.first()
    default_country_code = settings.default_country_code

    if default_country_code is None:
        log.info("default_country_code is not set, defaulting to US")
        default_country_code = "US"

    return default_country_code


def get_shop_default_currency_symbol():
    currency_code = get_shop_default_currency_code()
    currency_symbol = get_currency_symbol_from_currency_code(currency_code)
    return currency_symbol


def get_geo_country_code():
    # If geo country_code is set, use that,
    # otherwise fallback to shops default country_code
    if session.get("country_code"):
        country_code = session.get("country_code")
    else:
        country_code = get_shop_default_country_code()
    log.debug(f"get_geo_country_code returned country_code: {country_code}")
    return country_code


def get_currency_symbol_from_currency_code(currency_code: str) -> str:
    currency_code = currency_code.upper()
    currency_symbol = CurrencySymbols.get_symbol(currency_code)
    return currency_symbol


def get_geo_currency_symbol():
    """Return default currency symbol"""
    default_currency = get_geo_currency_code()
    if default_currency is None:
        default_currency = "USD"
    currency_symbol = CurrencySymbols.get_symbol(default_currency)
    return currency_symbol


def get_shop_default_currency_code():
    from subscribie.models import Setting

    """Return default shop currency code in iso_4217 format
       (e.g. GBP, USD)
    """
    setting = Setting.query.first()
    default_currency_code = setting.default_currency
    # Mid-upgrade compatibility for shops migrating before
    # https://github.com/Subscribie/subscribie/issues/482
    if default_currency_code is None:
        default_currency_code = "USD"
        log.info(
            f"No default_currency_code found, so falling back to {default_currency_code}"  # noqa: E501
        )

    return default_currency_code


def currencyFormat(currency_code: str, value) -> str:
    currency_symbol = get_currency_symbol_from_currency_code(currency_code)
    value = float(value) / 100
    units = "{:,.2f}".format(value)
    formatted_currency = f"{currency_symbol}{units}"
    return formatted_currency


def get_stripe_secret_key():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return settings.get("STRIPE_LIVE_SECRET_KEY", None)
    else:
        return settings.get("STRIPE_TEST_SECRET_KEY", None)


def get_stripe_publishable_key():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_livemode:
        return settings.get("STRIPE_LIVE_PUBLISHABLE_KEY", None)
    else:
        return settings.get("STRIPE_TEST_PUBLISHABLE_KEY", None)


def create_stripe_connect_account(company, country_code=None, default_currency=None):
    assert country_code is not None
    assert default_currency is not None

    stripe.api_key = get_stripe_secret_key()
    if "127.0.0.1" in request.host_url:
        url = "blackhole-1.iana.org"
    else:
        url = request.host_url

    account = stripe.Account.create(
        type="express",
        email=g.user.email,
        country=country_code,
        default_currency=default_currency,
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
    from subscribie.models import TaxRate

    # If there's no tax rate for current live mode create and save one:
    # if TaxRate.query.filter_by(stripe_livemode=livemode).first() is None:
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


def stripe_livemode():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_live_connect_account_id is not None:
        return True
    return False


def stripe_testmode():
    from .models import PaymentProvider

    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_test_connect_account_id is not None:
        return True
    return False


def announce_stripe_connect_account(account_id, live_mode=0):
    log.debug(f"Announcing stripe account to {url_for('index', _external=True)}")
    from subscribie.models import PaymentProvider  # noqa: F401

    ANNOUNCE_HOST = settings.get("STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST")
    req = requests.post(
        ANNOUNCE_HOST,
        json={
            "stripe_connect_account_id": account_id,
            "live_mode": live_mode,
            "site_url": url_for("index", _external=True),
        },
        timeout=10,
    )
    msg = {
        "msg": f"Announced Stripe connect account {account_id} \
for site_url {request.host_url}, to the STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST: \
{settings.get('STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST')}\n\
WARNING: Check logs to verify receipt"
    }
    log.debug(msg)
    req.raise_for_status()


@background_task
def get_stripe_invoices(app, last_n_days=30):
    """Upsert Stripe invoices into stripe_invoices

    Fetches all Stripe Invoices for a given connect customer,
    and inserts or updates the record into stripe_invoice
    table.

    This store is NOT currently synchronised live with Stipe, it
    is provided for speed to avoid round trip time.

    - See also models.StripeInvoice

    :param app: Required. The flask app, used for app context

    Currently this requires an app context, it is preferable to
    remove this dependency.
    """
    log.debug("get_stripe_invoices called")
    from subscribie.models import StripeInvoice, Subscription

    # Calculate the date last_n_days before today
    today = datetime.now()
    days_before_today = today - timedelta(days=last_n_days)
    days_before_today_timestamp = int(days_before_today.timestamp())

    # Remember: "Subscription" is a Subscribie model, not a Stripe one
    # because Subscribie does not assume all Subscriptions are from Stripe
    with app.app_context():
        stripe.api_key = get_stripe_secret_key()
        stripe_connect_account_id = get_stripe_connect_account_id()
        invoices = stripe.Invoice.list(
            stripe_account=stripe_connect_account_id,
            limit=100,
            created={"gte": days_before_today_timestamp},
        )
        for latest_stripe_invoice in invoices.auto_paging_iter():
            # Upsert each Stripe Invoice into stripe_invoice.
            # Check if invoice already exists, if it does, update the
            # record, else insert new row.
            # We perform the upsert operation manually because the primary key
            # is a uuid controlled by Subscribie, therefore the uuid will not
            # be present in the uuid from Stripe, however the Stripe controlled
            # Invoice.id will be, so we use that to query, then update or insert
            # based on if the invoice is already present or not.
            #
            # latestStripeInvoice - A invoice record from Stripe, this will be the
            #   most up to date.
            #
            # cachedStripeInvoice - The copy of the Stripe Invoice record in
            #   Subscribie's database, which may be out of date. We overwrite this with
            #   latestStripeInvoice.
            #
            # NOTE: Do not rely upon next_payment_attempt without checking the data
            # is not stale by performing a fetch from Stripe.
            #
            cachedStripeInvoice = StripeInvoice.query.where(
                StripeInvoice.id == latest_stripe_invoice.id
            ).first()
            if cachedStripeInvoice is not None:
                # Perform update, Stripe Invoice already present
                stripeInvoice = StripeInvoice.query.filter_by(
                    id=latest_stripe_invoice.id
                ).first()
                stripeInvoice.id = latest_stripe_invoice.id
                stripeInvoice.status = latest_stripe_invoice.status
                stripeInvoice.amount_due = latest_stripe_invoice.amount_due
                stripeInvoice.amount_paid = latest_stripe_invoice.amount_paid
                stripeInvoice.amount_remaining = latest_stripe_invoice.amount_remaining
                stripeInvoice.application_fee_amount = (
                    latest_stripe_invoice.application_fee_amount
                )
                stripeInvoice.attempt_count = latest_stripe_invoice.attempt_count
                stripeInvoice.next_payment_attempt = (
                    latest_stripe_invoice.next_payment_attempt
                )
                stripeInvoice.billing_reason = latest_stripe_invoice.billing_reason
                stripeInvoice.collection_method = (
                    latest_stripe_invoice.collection_method
                )
                stripeInvoice.currency = latest_stripe_invoice.currency
                stripeInvoice.stripe_subscription_id = (
                    latest_stripe_invoice.subscription
                )

                # created is invoice created date, created_at is the row creation date
                stripeInvoice.created = latest_stripe_invoice.created
                stripeInvoice.stripe_invoice_raw_json = latest_stripe_invoice.__str__()
                # Attach Subscribie subscription relationship if subscription it not None # noqa: E501
                subscribieSubscription = Subscription.query.where(
                    Subscription.stripe_subscription_id
                    == latest_stripe_invoice.subscription
                ).first()
                stripeInvoice.subscribie_subscription = subscribieSubscription
                database.session.commit()
                log.info(
                    f"Updating existing new cachedStripeInvoice {latest_stripe_invoice.id}"  # noqa: E501
                )
            elif cachedStripeInvoice is None:
                # Perform StripeInvoice insert, must be first time caching Stripe Invoice # noqa: E501
                log.info(f"Storing new cachedStripeInvoice {latest_stripe_invoice.id}")
                stripeInvoice = StripeInvoice()
                stripeInvoice.id = latest_stripe_invoice.id
                stripeInvoice.status = latest_stripe_invoice.status
                stripeInvoice.amount_due = latest_stripe_invoice.amount_due
                stripeInvoice.amount_paid = latest_stripe_invoice.amount_paid
                stripeInvoice.amount_remaining = latest_stripe_invoice.amount_remaining
                stripeInvoice.application_fee_amount = (
                    latest_stripe_invoice.application_fee_amount
                )
                stripeInvoice.attempt_count = latest_stripe_invoice.attempt_count
                stripeInvoice.next_payment_attempt = (
                    latest_stripe_invoice.next_payment_attempt
                )
                stripeInvoice.billing_reason = latest_stripe_invoice.billing_reason
                stripeInvoice.collection_method = (
                    latest_stripe_invoice.collection_method
                )
                stripeInvoice.currency = latest_stripe_invoice.currency
                stripeInvoice.stripe_subscription_id = (
                    latest_stripe_invoice.subscription
                )
                # created is invoice created date, created_at is the row creation date
                stripeInvoice.created = latest_stripe_invoice.created
                stripeInvoice.stripe_invoice_raw_json = latest_stripe_invoice.__str__()
                # Attach Subscribie subscription relationship if subscription it not None # noqa: E501
                subscribieSubscription = Subscription.query.where(
                    Subscription.stripe_subscription_id
                    == latest_stripe_invoice.subscription
                ).first()
                stripeInvoice.subscribie_subscription = subscribieSubscription
                database.session.add(stripeInvoice)
                database.session.commit()
    log.debug("Finished get_stripe_invoices")


def stripe_invoice_failed(stripeInvoice):
    """Returns true/false if a Stripe Invoice has failed all collection attempts
    and no further *automated* collection will take place."""
    if stripeInvoice.subscribie_subscription_id:
        if (
            stripeInvoice.status == "open"
            and stripeInvoice.next_payment_attempt is None
        ):
            log.debug(f"Returning True for stripe_invoice_failed: {stripeInvoice}")
            return True
    else:
        return False


def stripe_invoice_failing(stripeInvoice):
    """Returns true/false if a Stripe Invoice is failing
    NOTE: Automatic payment attempts may still happen
    for a failing invoice- see stripe_invoice_failed
    for failed invoice check
    """
    if stripeInvoice.subscribie_subscription_id:
        if (
            stripeInvoice.status == "open"
            and stripeInvoice.next_payment_attempt is not None
        ):
            log.debug(f"Returning True for stripe_invoice_failing: {stripeInvoice}")
            return True
    else:
        return False


def getBadInvoices():
    """Return both failed and failing invoices

    What's a bad invoice?

    A bad invoice is either one which is failing or failed
    """
    failingInvoices = get_stripe_failing_subscription_invoices()
    failedInvoices = get_stripe_failed_subscription_invoices()

    badInvoices = failingInvoices + failedInvoices

    return badInvoices


def get_stripe_failing_subscription_invoices():
    """Return list of stripe failing invoices
    Note: remember that failing invoices may still
    get automatic attempts to be collected
    """
    failingInvoices = []
    from subscribie.models import StripeInvoice

    log.info("Fetching Stripe failing Invoices from database cache")

    stripeInvoices = StripeInvoice.query.all()
    for stripeInvoice in stripeInvoices:
        if stripe_invoice_failing(stripeInvoice):
            log.info(
                f"appending failing Stripe Invoice {stripeInvoice.id} to failingInvoices from cache"  # noqa: E501
            )
            failingInvoices.append(stripeInvoice)
    return failingInvoices


def get_stripe_failed_subscription_invoices():
    """Return Stripe invoices which have failed, and
    were generated via a Stripe Subscription."""

    failedInvoices = []
    from subscribie.models import StripeInvoice

    log.info("Fetching Stripe failed Invoices from database cache")

    stripeInvoices = StripeInvoice.query.all()
    for stripeInvoice in stripeInvoices:
        if stripe_invoice_failed(stripeInvoice):
            log.info(
                f"appending failed Stripe Invoice {stripeInvoice.id} to failedInvoices from cache"  # noqa: E501
            )
            # Means invoice is no longer being auto collected
            failedInvoices.append(stripeInvoice)
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


def get_discount_code():
    """Get discount code from the current session
    :return: The discount code, or None
    :rtype: str
    """
    return session.get("discount_code", None)


def dec2pence(amount: str) -> int:
    """Take a two decimal place string and convert to pence"""
    from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

    if not amount:
        return 0
    try:
        # Using ROUND_HALF_UP for typical financial rounding
        pence = Decimal(amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100
        return int(pence)
    except (ValueError, InvalidOperation):
        raise ValueError(
            "Invalid input: amount should be a string representing a decimal number"
        )


def backfill_transactions(days=30):
    """Backfill transaction data in an idempotent way
    Useful for fixing webhook delivery misses (such as if all webhook delivery retires
    exhausted), and data corrections from Hotfixes.

    - Upserts Transaction records from Stripe PaymentIntents
    - .e.g created_at See https://github.com/Subscribie/subscribie/issues/1385
    """
    from subscribie.models import Transaction, Subscription, Person

    stripe_connect_account_id = get_stripe_connect_account_id()

    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    today = datetime.now()
    days_before_today = today - timedelta(days=days)
    days_before_today_timestamp = int(days_before_today.timestamp())
    paymentIntents = stripe.PaymentIntent.list(
        stripe_account=stripe_connect_account_id,
        limit=100,
        created={"gte": days_before_today_timestamp},
    )

    created_count = 0
    updated_count = 0

    for paymentIntent in paymentIntents.auto_paging_iter():
        transaction = (
            database.session.query(Transaction)
            .filter_by(external_id=paymentIntent.id)
            .first()
        )
        # Get transaction related invoice & subscription_id if available
        if paymentIntent.invoice:
            try:
                invoice = stripe.Invoice.retrieve(
                    stripe_account=stripe_connect_account_id,
                    id=paymentIntent.invoice
                )
                if invoice.subscription:
                    subscription_id = invoice.subscription
            except Exception as e:
                log.warning(f"Could not retrieve invoice {paymentIntent.invoice}: {e}")

        stripe_transaction_created_at = datetime.fromtimestamp(paymentIntent.created)

        if transaction is not None:
            # Update existing transaction
            msg = f"Updating transaction.id {transaction.id} (external_id: {paymentIntent.id})"
            log.info(msg)

            # Update created_at if different
            if transaction.created_at != stripe_transaction_created_at:
                msg = f"Setting transaction.id {transaction.id} created_at to {stripe_transaction_created_at}"
                log.info(msg)
                transaction.created_at = stripe_transaction_created_at

            # Update other fields that may have changed
            transaction.amount = paymentIntent.amount
            transaction.currency = paymentIntent.currency
            transaction.payment_status = "paid" if paymentIntent.status == "succeeded" else paymentIntent.status

            database.session.commit()
            updated_count += 1
        else:
            # Create new transaction
            log.info(f"Creating new transaction for PaymentIntent {paymentIntent.id}")
            transaction = Transaction()
            transaction.external_id = paymentIntent.id
            transaction.external_src = "stripe"
            transaction.currency = paymentIntent.currency
            transaction.amount = paymentIntent.amount
            transaction.payment_status = "paid" if paymentIntent.status == "succeeded" else paymentIntent.status
            transaction.comment = invoice.subscription_details.metadata.get("donation_comment") if invoice and invoice.subscription_details  else None
            transaction.created_at = stripe_transaction_created_at

            # Try to find subscription in local database
            if subscription_id:
                subscribie_subscription = (
                    database.session.query(Subscription)
                    .filter_by(stripe_subscription_id=subscription_id)
                    .first()
                )
                if subscribie_subscription:
                    transaction.subscription = subscribie_subscription
                    transaction.person = subscribie_subscription.person
                    log.info(f"Linked transaction to subscription {subscribie_subscription.id}")
                else:
                    log.warning(f"Subscription {subscription_id} not found in local database")

            # Try to get person from metadata if no subscription found
            if transaction.person is None and paymentIntent.invoice:
                person_uuid = invoice.subscription_details.metadata.get("person_uuid") if invoice and invoice.subscription_details else None
                if person_uuid:
                    person = Person.query.filter_by(uuid=person_uuid).first()
                    if person:
                        transaction.person = person
                        log.info(f"Linked transaction to person {person.id} via metadata")

                # Check if it's a donation
                is_donation = invoice.subscription_details.metadata.get("is_donation", "False") if invoice and invoice.subscription_details else False
                if is_donation == "True":
                    transaction.is_donation = True

            database.session.add(transaction)
            database.session.commit()
            created_count += 1

    log.info(f"Backfill complete: {created_count} transactions created, {updated_count} updated")


def backfill_subscriptions(days=30):
    """Backfill subscription data in an idempotent way
    Useful for fixing webhook delivery misses (such as if all webhook delivery retires
    exhausted), and data corrections from Hotfixes.

    - .e.g created_at See https://github.com/Subscribie/subscribie/issues/1385
    """
    from subscribie.models import Subscription

    stripe_connect_account_id = get_stripe_connect_account_id()

    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    today = datetime.now()
    days_before_today = today - timedelta(days=days)
    days_before_today_timestamp = int(days_before_today.timestamp())
    subscriptions = stripe.Subscription.list(
        stripe_account=stripe_connect_account_id,
        limit=100,
        created={"gte": days_before_today_timestamp},
    )
    for stripe_subscription in subscriptions.auto_paging_iter():
        subscribie_subscription = (
            database.session.query(Subscription)
            .filter_by(stripe_subscription_id=stripe_subscription.id)
            .first()
        )

        if subscribie_subscription is not None:
            # Update the subscribie_subscription in Subscription model
            msg = f"Current subscription.id {subscribie_subscription.id} created_at: {subscribie_subscription.created_at}"  # noqa: E501
            log.info(msg)

            # TODO Stripe incorporate subscription.start_date into Subscription model
            # https://docs.stripe.com/api/subscriptions/object#subscription_object-start_date
            stripe_subscription_created_at = datetime.fromtimestamp(
                stripe_subscription.created
            )  # noqa: E501
            msg = f"Upstream subscription.id {subscribie_subscription.id} created_at set to {stripe_subscription_created_at}"  # noqa: E501
            log.info(msg)

            if subscribie_subscription.created_at != stripe_subscription_created_at:
                msg = f"Setting subscription.id {subscribie_subscription.id} created_at to {stripe_subscription_created_at}"  # noqa: E501
                log.info(msg)
                subscribie_subscription.created_at = stripe_subscription_created_at
                database.session.commit()
            else:
                log.info(
                    "Skipping subscription.created_at update for subscription id {subscribie_subscription.id} as source data is equal to local"  # noqa: E501
                )  # noqa: E501


def backfill_persons(days=30):
    """Backfill person data in an idempotent way
    Useful for fixing webhook delivery misses (such as if all webhook delivery retires
    exhausted), and data corrections from Hotfixes.

    NOTE: The Stripe session checkout object is used here to
    signify the earliest known date/time for Person.created_at time
    since a Person record is created during checkout, this is a reasonable
    source for created_at time during a backfill recovery run.

    - .e.g created_at See https://github.com/Subscribie/subscribie/issues/1385

    Subscribie stores checkout metadata useful for associating checkouts with
    a person on the Subscription table(see models.py) these fields include:

    - subscribie_checkout_session_id
    - stripe_external_id
    - stripe_subscription_id
    And a Subscription object is *always* linked to a Person entity.

    """
    from subscribie.models import Subscription

    stripe_connect_account_id = get_stripe_connect_account_id()

    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    today = datetime.now()
    days_before_today = today - timedelta(days=days)
    days_before_today_timestamp = int(days_before_today.timestamp())
    stripe_checkout_sessions = stripe.checkout.Session.list(
        stripe_account=stripe_connect_account_id,
        limit=100,
        created={"gte": days_before_today_timestamp},
    )
    for stripe_session in stripe_checkout_sessions.auto_paging_iter():
        if stripe_session.metadata.get("subscribie_checkout_session_id") is None:
            log.warning(
                f"No subscribie_checkout_session_id found on metadata for stripe_session {stripe_session.id}"  # noqa: E501
            )  # noqa: E501
            continue

        subscribie_subscription = (
            database.session.query(Subscription)
            .filter_by(
                subscribie_checkout_session_id=stripe_session.metadata[
                    "subscribie_checkout_session_id"
                ]
            )
            .first()
        )
        if subscribie_subscription is not None:
            if subscribie_subscription.person is None:
                log.warning(
                    f"Skipping stripe_session {stripe_session.id} as person is None for subscription {subscribie_subscription.id}"  # noqa: E501
                )  # noqa: E501
                continue
            # Update the subscribie_subscription in Subscription model
            log.debug(f"At stripe_session.id: {stripe_session.id}")
            msg = f"Current person.created_at: {subscribie_subscription.person.created_at}"  # noqa: E501
            log.info(msg)

            # TODO Stripe incorporate subscription.start_date into Subscription model
            # https://docs.stripe.com/api/subscriptions/object#subscription_object-start_date
            stripe_session_created_at = datetime.fromtimestamp(
                stripe_session.created
            )  # noqa: E501
            msg = f"Inferring person create_at from stripe_session_created_at: {stripe_session_created_at}"  # noqa: E501
            log.info(msg)
            msg = f"Setting person.created_at to {stripe_session_created_at}"  # noqa: E501
            log.info(msg)
            subscribie_subscription.person.created_at = stripe_session_created_at
            database.session.commit()


def backfill_stripe_invoices(days=30):
    """Backfill stripe_invoice data in an idempotent way
    Useful for fixing webhook delivery misses (such as if all webhook delivery retires
    exhausted), and data corrections from Hotfixes.

    - .e.g created_at See https://github.com/Subscribie/subscribie/issues/1385

    """
    from subscribie.models import StripeInvoice

    stripe_connect_account_id = get_stripe_connect_account_id()

    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    today = datetime.now()
    days_before_today = today - timedelta(days=days)
    days_before_today_timestamp = int(days_before_today.timestamp())
    stripe_invoices = stripe.Invoice.list(
        stripe_account=stripe_connect_account_id,
        limit=100,
        created={"gte": days_before_today_timestamp},
    )
    for stripe_invoice in stripe_invoices.auto_paging_iter():

        local_stripe_invoice = (
            database.session.query(StripeInvoice)
            .filter_by(id=stripe_invoice.id)
            .first()
        )
        if local_stripe_invoice is not None:
            # Update the local_stripe_invoice in StripeInvoice model
            log.debug(f"At local_stripe_invoice.id: {local_stripe_invoice.id}")
            msg = f"Current local_stripe_invoice.created_at: {local_stripe_invoice.created_at}"  # noqa: E501
            log.info(msg)

            stripe_invoice_created_at = datetime.fromtimestamp(
                stripe_invoice.created
            )  # noqa: E501
            msg = f"stripe_invoice create_at: {stripe_invoice_created_at}"  # noqa: E501
            log.info(msg)
            msg = f"Setting local_stripe_invoice.created_at to {stripe_invoice_created_at}"  # noqa: E501
            log.info(msg)
            local_stripe_invoice.created_at = stripe_invoice_created_at
            database.session.commit()


def get_mailchimp_list_name(list_id: str) -> str:
    """
    Internally (api) mailchimp calls lists
    Externally (human facing) mailchimp calls
    lists 'audiences'
    """
    from subscribie.models import Integration
    from requests.auth import HTTPBasicAuth

    mailchimp_audience_name = None
    integration = Integration.query.first()
    try:
        mailchimp_api_key, dc = integration.mailchimp_api_key.split("-")

        if integration.mailchimp_active:
            url = f"https://{dc}.api.mailchimp.com/3.0/lists/{list_id}"

            # Make the GET request
            response = requests.get(
                url, auth=HTTPBasicAuth("anystring", mailchimp_api_key)
            )

            # Return the name of the list from the JSON response
            mailchimp_audience_name = response.json().get("name")
    except Exception as e:
        log.error(f"Could not get_mailchimp_list_name: {e}")

    return mailchimp_audience_name
