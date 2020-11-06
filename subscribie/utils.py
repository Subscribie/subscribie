from subscribie.models import PaymentProvider, Company
from subscribie.database import database
from flask import current_app, request, g, url_for, flash
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


def create_stripe_connect_account(company: Company):
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


def create_stripe_webhook():
    """
    Creates a new webhook, deleting old one if invalid
    """

    if "127.0.0.1" in request.host or "localhost" in request.host:
        flash(
            "Refusing to create Stripe webhook on localhost, use stripe cli for local development"  # noqa
        )
        # return False

    stripe.api_key = get_stripe_secret_key()
    webhook_url = url_for("views.stripe_webhook", _external=True)
    webhook_url = "https://testing.subscriby.shop/stripe_webhook"

    payment_provider = PaymentProvider.query.first()
    newWebhookNeeded = False

    liveMode = payment_provider.stripe_livemode  # returns bool

    if liveMode:
        webhook_id = payment_provider.stripe_live_webhook_endpoint_id
    else:
        webhook_id = payment_provider.stripe_test_webhook_endpoint_id

    if webhook_id is None:
        newWebhookNeeded = True

    # Try to get current webhook
    try:
        stripe.WebhookEndpoint.retrieve(webhook_id)
    except stripe.error.InvalidRequestError as e:
        print(e)
        print(f"Creating new Stripe webhook in mode {liveMode}")
        newWebhookNeeded = True

    if newWebhookNeeded:
        # Delete previous webhooks which match the webhook_url
        webhooks = stripe.WebhookEndpoint.list()
        for webhook in webhooks:
            # Only delete webhook if matched url and same live mode state (true/false)
            if webhook.url == webhook_url and webhook.livemode == liveMode:
                stripe.WebhookEndpoint.delete(webhook.id)

        # Create a new webhook
        try:
            webhook_endpoint = stripe.WebhookEndpoint.create(
                url=webhook_url,
                enabled_events=[
                    "*",
                ],
                description="Subscribie webhook endpoint",
                connect=True,  # endpoint should receive events from connected accounts
            )
            # Store the webhook secret & webhook id
            if payment_provider.stripe_livemode:
                payment_provider.stripe_live_webhook_endpoint_id = webhook_endpoint.id
                payment_provider.stripe_live_webhook_endpoint_secret = (
                    webhook_endpoint.secret
                )
                print(
                    f"New live webhook id is: {payment_provider.stripe_live_webhook_endpoint_id}"  # noqa
                )
            else:
                payment_provider.stripe_test_webhook_endpoint_id = webhook_endpoint.id
                payment_provider.stripe_test_webhook_endpoint_secret = (
                    webhook_endpoint.secret
                )
                print(
                    f"New test webhook id is: {payment_provider.stripe_test_webhook_endpoint_id}"  # noqa
                )

        except stripe.error.InvalidRequestError as e:
            print(e)
            flash("Error trying to create Stripe webhook")
            payment_provider.stripe_active = False
    database.session.commit()
