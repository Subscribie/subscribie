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
               <button class="btn btn-primary" hx-get="{url_for('admin.edit_subscriber_email', subscriber_id=person.id)}">
                Edit
               </button>
              </li>
            </span>
           """


def show_subscriber_full_name(subscriber_id):
    person = Person.query.execution_options(include_archived=True).get(subscriber_id)

    return f"""
            <span hx-target="this" hx-swap="outerHTML">
            <h3 class="card-title">👤 {person.full_name}</h3>
            <button hx-get="{url_for('admin.edit_subscriber_full_name', subscriber_id=person.id)}" class="btn btn-primary">Edit</button>
            </span>
           """


@admin.route("/subscriber/<subscriber_id>/email", methods=["GET"])
@login_required
def get_subscriber_email_address(subscriber_id):
    return show_subscriber_email(subscriber_id)


@admin.route("/subscriber/<subscriber_id>/full_name", methods=["GET"])
@login_required
def get_subscriber_full_name(subscriber_id):
    return show_subscriber_full_name(subscriber_id)


@admin.route("/subscriber/<subscriber_id>/email/edit", methods=["GET", "PUT"])
@login_required
def edit_subscriber_email(subscriber_id):
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
    <form hx-put="{url_for('admin.edit_subscriber_email', subscriber_id=subscriber_id)}" hx-target="this" hx-swap="outerHTML">
    <div class="form-group">
        <label>Email Address</label>
        <input type="email" name="email" value="{person.email}">
    </div>
    <button class="btn btn-primary">Submit</button>
    <button class="btn"
    hx-get="{url_for('admin.get_subscriber_email_address', subscriber_id=subscriber_id)}">Cancel</button>
    </form>
    """


@admin.route("/subscriber/<subscriber_id>/full_name/edit", methods=["GET", "PUT"])
@login_required
def edit_subscriber_full_name(subscriber_id):
    person = Person.query.execution_options(include_archived=True).get(subscriber_id)

    if request.method == "PUT":
        old_given_name = person.given_name
        old_family_name = person.family_name
        new_given_name = request.form.get("given_name")
        new_family_name = request.form.get("family_name")
        person.given_name = new_given_name
        person.family_name = new_family_name

        database.session.commit()

        # Also update Stripe customer email record
        try:
            if len(person.subscriptions) > 0:
                # Verify we have a Stripe customer record for
                # this person (a person may have subscriptions,
                # however they may not all be associated with Stripe)
                # e.g. Free subscriptions, other payment providers etc.
                log.debug("Verifying if person has associated Stripe record or not")
                if len(person.subscriptions[0].stripe_invoices) > 0:
                    new_name = f"{new_given_name} {new_family_name}"
                    stripe_customer_id = json.loads(
                        person.subscriptions[0]
                        .stripe_invoices[0]
                        .stripe_invoice_raw_json
                    )["customer"]
                    stripe.api_key = get_stripe_secret_key()
                    stripe_connect_account_id = get_stripe_connect_account_id()
                    stripe.Customer.modify(
                        id=stripe_customer_id,
                        stripe_account=stripe_connect_account_id,
                        name=new_name,
                    )
                else:
                    msg = f"""Updating Person {person.id} full_name however no Stripe
                    record found. This may be OK if no associated Stripe payments"""
                    log.warning(msg)
        except Exception as e:
            log.error(f"Failure updating person '{person.id}' full_name to. {e}")
            log.debug(
                "Switching person given_name / family_name address back to previous values"
            )
            person.given_name = old_given_name
            person.family_name = old_family_name
            database.session.commit()

        return show_subscriber_full_name(subscriber_id)

    return f"""
    <form hx-put="{url_for('admin.edit_subscriber_full_name', subscriber_id=subscriber_id)}" hx-target="this" hx-swap="outerHTML">
    <div class="form-group">
        <label>First name:</label>
        <input type="text" name="given_name" value="{person.given_name}">
    </div>
    <div class="form-group">
        <label>Last name:</label>
        <input type="text" name="family_name" value="{person.family_name}">
    </div>
    <button class="btn btn-primary">Submit</button>
    <button class="btn"
    hx-get="{url_for('admin.get_subscriber_full_name', subscriber_id=subscriber_id)}">Cancel</button>
    </form>
    """


@admin.route("/charge/subscriber/<person_id>", methods=["GET"])
@login_required
def charge_subscriber(person_id):
    person = Person.query.get(person_id)
    return render_template("admin/subscriber/charge_subscriber.html", person=person)
