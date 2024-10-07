from . import admin
from subscribie.auth import login_required
from subscribie.models import Person
from flask import render_template, url_for, request
from subscribie.utils import get_stripe_secret_key, get_stripe_connect_account_id
from subscribie.database import database
import stripe
import json
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
            stripe_invoice = stripe.Invoice.retrieve(
                id=open_invoice.id, stripe_account=stripe_connect_account_id
            )
            setattr(
                open_invoices[index],
                "hosted_invoice_url",
                stripe_invoice.hosted_invoice_url,
            )
    except Exception as e:
        log.error(
            f"Unable to get/set hosted_invoice_url for invoice: {open_invoice.id}. {e}"
        )

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


def show_subscriber_email(subscriber_id):
    person = Person.query.execution_options(include_archived=True).get(subscriber_id)

    return f"""
            <span hx-target="this" hx-swap="outerHTML">
              <li class="list-group-item">📧 {person.email}
               <button hx-get="{url_for('admin.edit_subscriber', subscriber_id=person.id)}">
                Edit
               </button>
              </li>
            </span>
           """


@admin.route("/subscriber/<subscriber_id>/email", methods=["GET"])
@login_required
def get_subscriber_email_address(subscriber_id):
    return show_subscriber_email(subscriber_id)


@admin.route("/subscriber/<subscriber_id>/edit", methods=["GET", "PUT"])
@login_required
def edit_subscriber(subscriber_id):
    person = Person.query.execution_options(include_archived=True).get(subscriber_id)

    if request.method == "PUT":
        old_email = person.email
        new_email = request.form.get("email")
        person.email = new_email
        database.session.commit()

        # Also update Stripe customer email record
        try:
            if len(person.subscriptions) > 0:
                stripe_customer_id = json.loads(
                    person.subscriptions[0].stripe_invoices[0].stripe_invoice_raw_json
                )["customer"]
                stripe.api_key = get_stripe_secret_key()
                stripe_connect_account_id = get_stripe_connect_account_id()
                stripe.Customer.modify(
                    id=stripe_customer_id,
                    stripe_account=stripe_connect_account_id,
                    email=new_email,
                )
        except Exception as e:
            log.error(
                f"Failure updating person '{person.id}' email to {new_email}. {e}"
            )
            log.debug("Switching person email address back to old email")
            person.email = old_email
            database.session.commit()

        return show_subscriber_email(subscriber_id)

    return f"""
    <form hx-put="{url_for('admin.edit_subscriber', subscriber_id=subscriber_id)}" hx-target="this" hx-swap="outerHTML">
    <div class="form-group">
        <label>Email Address</label>
        <input type="email" name="email" value="{person.email}">
    </div>
    <button class="btn btn-primary">Submit</button>
    <button class="btn btn-secondary"
    hx-get="{url_for('admin.get_subscriber_email_address', subscriber_id=subscriber_id)}">Cancel</button>
    </form>
    """


@admin.route("/charge/subscriber/<person_id>", methods=["GET"])
@login_required
def charge_subscriber(person_id):
    person = Person.query.get(person_id)
    return render_template("admin/subscriber/charge_subscriber.html", person=person)
