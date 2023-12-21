from . import admin
from subscribie.auth import login_required
from subscribie.models import Person
from flask import render_template
import logging

log = logging.getLogger(__name__)


@admin.route("/show-subscriber/<subscriber_id>", methods=["GET", "POST"])
@login_required
def show_subscriber(subscriber_id):
    person = Person.query.execution_options(include_archived=True).get(subscriber_id)
    customer_balance_list = person.balance()  # See models.py 'class Person'
    invoices = person.invoices()
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
        customer_balance_list=customer_balance_list,
        collection_decline_codes=set(collection_decline_codes),
    )


@admin.route("/charge/subscriber/<person_id>", methods=["GET"])
@login_required
def charge_subscriber(person_id):
    person = Person.query.get(person_id)
    return render_template("admin/subscriber/charge_subscriber.html", person=person)
