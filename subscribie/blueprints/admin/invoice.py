from . import admin
import json
import logging
from subscribie.auth import login_required, stripe_connect_id_required
from subscribie.database import database
from subscribie.models import UpcomingInvoice, Subscription, StripeInvoice, Person
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account,
    get_stripe_connect_account_id,
)
from subscribie.utils import (
    get_stripe_invoices,
)
from flask import render_template, flash, request, redirect, url_for
import stripe

log = logging.getLogger(__name__)


@admin.route("/invoices/failed/", methods=["GET"])
@login_required
@stripe_connect_id_required
def failed_invoices():
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    if "refreshFailedInvoices" in request.args:
        flash("Invoice statuses are being refreshed")
        get_stripe_invoices()

    # Get failed invoices, grouped by person and their invoices
    failedInvoices = (
        database.session.query(StripeInvoice)
        .join(Subscription, StripeInvoice.subscribie_subscription)
        .join(Person, Subscription.person)
        .group_by(Person.id, StripeInvoice.id)
        .where(StripeInvoice.status == "open")
        .where(StripeInvoice.next_payment_attempt == None)  # noqa: E711
        .execution_options(include_archived=True)
        .order_by(Person.given_name)
        .all()
    )
    # Build dictionary of person uuid -> (bad) invoices so
    # that it's easier for template to display bad invoices broken down
    # per person
    subscribersWithFailedInvoicesMap = {}

    for failedInvoice in failedInvoices:
        # Populate map with each Person.uuid
        if (
            failedInvoice.subscribie_subscription.person.uuid
            not in subscribersWithFailedInvoicesMap
        ):
            # Create person uuid key in map
            subscribersWithFailedInvoicesMap[
                failedInvoice.subscribie_subscription.person.uuid
            ] = {}
            # Create empty list to store persons bad invoices
            subscribersWithFailedInvoicesMap[
                failedInvoice.subscribie_subscription.person.uuid
            ]["failedInvoices"] = []

            # Create reference to person object via invoice reference
            subscribersWithFailedInvoicesMap[
                failedInvoice.subscribie_subscription.person.uuid
            ]["person"] = failedInvoice.subscribie_subscription.person

        # Add hosted_invoice_url attribute to invoice
        try:
            stripe_invoice = stripe.Invoice.retrieve(
                id=failedInvoice.id, stripe_account=stripe_connect_account_id
            )
            setattr(
                failedInvoice,
                "hosted_invoice_url",
                stripe_invoice.hosted_invoice_url,
            )
        except Exception as e:
            log.error(
                f"Unable to get/set hosted_invoice_url for invoice: {failedInvoice.id}. {e}"  # noqa: E501
            )

        # Get stripe_decline_code if possible
        try:
            stripeRawInvoice = json.loads(failedInvoice.stripe_invoice_raw_json)

            payment_intent_id = stripeRawInvoice["payment_intent"]
            stripe_decline_code = stripe.PaymentIntent.retrieve(
                payment_intent_id,
                stripe_account=stripe_connect_account_id,
            ).last_payment_error.decline_code
            setattr(failedInvoice, "stripe_decline_code", stripe_decline_code)
        except Exception as e:
            log.debug(
                f"Failed to get stripe_decline_code for invoice {failedInvoice.id}. Exeption: {e}"  # noqa: E501
            )

        # Insert invoices per person
        subscribersWithFailedInvoicesMap[
            failedInvoice.subscribie_subscription.person.uuid
        ]["failedInvoices"].append(failedInvoice)

    return render_template(
        "admin/invoice/failed_invoices.html",
        debtors=subscribersWithFailedInvoicesMap,
    )


@admin.route("/download-invoice/<invoice_id>", methods=["GET"])
@login_required
def download_invoice(invoice_id:str):
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()

    try:
        stripe_invoice = stripe.Invoice.retrieve(
            id=invoice_id, stripe_account=stripe_connect_account_id
        )
        return redirect(stripe_invoice.hosted_invoice_url)
    except stripe._error.InvalidRequestError as e:
        msg = f"Unable to download invoice {e}"
        log.error(msg)
        return msg


@admin.route("/fetch-upcoming_invoices")
def fetch_upcoming_invoices():
    fetch_stripe_upcoming_invoices()
    msg = "Upcoming invoices fetched."
    flash(msg)
    if request.referrer is not None:
        return redirect(url_for("admin.invoices"))
    return msg


def fetch_stripe_upcoming_invoices():
    """Fetch all Stripe upcoming invoices and populate the invoices table"""
    all_subscriptions = Subscription.query.all()
    upcoming_invoices = []
    stripe.api_key = get_stripe_secret_key()
    connect_account = get_stripe_connect_account()

    # Prepare to delete all previous upcomingInvoice
    UpcomingInvoice.query.delete()  # don't commit until finished fetching latest collection # noqa
    for subscription in all_subscriptions:
        try:
            log.info(
                f"Getting upcoming invoice for Stripe subscription: {subscription.stripe_subscription_id}"  # noqa
            )
            if subscription.stripe_subscription_id is not None:
                upcoming_invoice = stripe.Invoice.upcoming(
                    subscription=subscription.stripe_subscription_id,
                    stripe_account=connect_account.id,
                )
                upcoming_invoices.append(upcoming_invoice)
                # Store the UpcomingInvoice
                upcomingInvoice = UpcomingInvoice()
                upcomingInvoice.subscription = subscription
                upcomingInvoice.stripe_invoice_id = None
                upcomingInvoice.stripe_subscription_id = (
                    subscription.stripe_subscription_id
                )
                upcomingInvoice.stripe_invoice_status = upcoming_invoice.status
                upcomingInvoice.stripe_amount_due = upcoming_invoice.amount_due
                upcomingInvoice.stripe_amount_paid = upcoming_invoice.amount_paid
                upcomingInvoice.stripe_next_payment_attempt = (
                    upcoming_invoice.next_payment_attempt
                )
                upcomingInvoice.stripe_currency = upcoming_invoice.currency

                database.session.add(upcomingInvoice)

        except stripe.error.InvalidRequestError as e:
            log.error(
                f"Cannot get stripe subscription id: {subscription.stripe_subscription_id}, {e}"  # noqa
            )
        except Exception as e:
            log.error(f"Error checking for upcoming invoice for {subscription.id}, {e}")
        database.session.commit()
