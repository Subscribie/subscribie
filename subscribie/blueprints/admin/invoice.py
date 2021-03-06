import logging
from subscribie.database import database
from subscribie.models import UpcomingInvoice, Subscription
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account,
)
import stripe

log = logging.getLogger(__name__)


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
