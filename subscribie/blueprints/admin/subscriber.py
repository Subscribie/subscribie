from . import admin
from subscribie.auth import login_required
from subscribie.models import Person
from flask import render_template
from subscribie.utils import get_stripe_secret_key, get_stripe_connect_account, get_stripe_connect_account_id
import stripe
import logging

log = logging.getLogger(__name__)


@admin.route("/show-subscriber/<subscriber_id>", methods=["GET", "POST"])
@login_required
def show_subscriber(subscriber_id):
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()

    person = Person.query.execution_options(include_archived=True).get(subscriber_id)
    customer_balance_list = person.balance()  # See models.py 'class Person'
    invoices = person.invoices()
    open_invoices = person.failed_invoices()
    # Add hosted_invoice_url attribute to all open invoices
    try:
        for index, open_invoice in enumerate(open_invoices):
            stripe_invoice = stripe.Invoice.retrieve(id=open_invoice.id, stripe_account=stripe_connect_account_id)
            setattr(open_invoices[index], 'hosted_invoice_url', stripe_invoice.hosted_invoice_url)
    except Exception as e:
        log.error(f"Unable to get/set hosted_invoice_url for invoice: {open_invoice.id}. {e}")

    # Try to be helpful to the shop owner by highlighting recent payment
    # payment stripe_decline_code errors (if any).
    collection_decline_codes = []
    for invoice in invoices:
        try:
            collection_decline_codes.append(invoice.stripe_decline_code)
        except AttributeError:
            pass

    return render_template(
        "admin/subscriber/show_subscriber.html",
        person=person,
        invoices=invoices,
        open_invoices=open_invoices,
        customer_balance_list=customer_balance_list,
        collection_decline_codes=set(collection_decline_codes),
    )


@admin.route("/charge/subscriber/<person_id>", methods=["GET"])
@login_required
def charge_subscriber(person_id):
    person = Person.query.get(person_id)
    return render_template("admin/subscriber/charge_subscriber.html", person=person)
