import logging
import stripe
import functools
import binascii
import os
from pathlib import Path
import flask
from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    session,
    g,
    current_app,
    request,
    Markup,
)
from subscribie.forms import (
    PasswordLoginForm,
    SubscriberForgotPasswordForm,
    SubscriberResetPasswordForm,
)
from subscribie.models import (
    Subscription,
    database,
    Person,
    Company,
    Option,
    ChosenOption,
    File,
    User,
    Plan,
    PlanRequirements,
)
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account_id,
    get_stripe_publishable_key,
)
from subscribie.email import EmailMessageQueue
from jinja2 import Template
import requests

log = logging.getLogger(__name__)
subscriber = Blueprint(
    "subscriber", __name__, template_folder="templates", url_prefix=None
)


@subscriber.before_app_request
def load_logged_in_subscriber():
    subscriber_id = session.get("subscriber_id")

    if subscriber_id is None:
        g.subscriber = None
    else:
        g.subscriber = Person.query.filter_by(email=subscriber_id).first()


def subscriber_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.subscriber is None:
            return redirect(url_for("subscriber.login"))

        return view(**kwargs)

    return wrapped_view


def check_password_login(email, password):
    subscriber = Person.query.filter_by(email=email).first()
    if subscriber.check_password(password):
        return True
    return False


@subscriber.route("/account/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if request.args.get("email"):
            email = request.args.get("email")
            # Check if password expired, send password reset email if expired.
            subscriber = Person.query.filter_by(email=email).first()
            if subscriber is not None and subscriber.password_expired:
                requests.post(
                    url_for("subscriber.forgot_password", _external=True),
                    data={"email": email},
                )
                flash("Please check your email & spam for a password reset email")

    form = PasswordLoginForm()
    if form.validate_on_submit():
        email = form.data["email"]
        password = form.data["password"]
        subscriber = Person.query.filter_by(email=email).first()
        if subscriber is None:
            shopowner = User.query.filter_by(email=email).first()
            if shopowner is not None:
                flash("You are a shop admin, please login here")
                return redirect(url_for("auth.login", email=email))
            flash("Person not found with that email")
            return redirect(url_for("subscriber.login"))
        if subscriber.password is None:
            msg = Markup(
                f"Password not set. Please <a href='{url_for('subscriber.forgot_password')}'>change your password.</a>"  # noqa: E501
            )
            flash(msg)
            return redirect(url_for("subscriber.login"))

        if check_password_login(email, password):
            session.clear()
            session["subscriber_id"] = subscriber.email
            return redirect(url_for("subscriber.account"))
        else:
            session.clear()
            flash("Invalid password")
            return redirect(url_for("subscriber.login"))
    return render_template("subscriber/login.html", form=form)


@subscriber.route("/account/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = SubscriberForgotPasswordForm()
    if form.validate_on_submit() or form.data.get("email"):
        email = form.data["email"]
        subscriber = Person.query.filter_by(email=email).first()
        if subscriber is None:
            flash("Person not found with that email")
            return redirect(url_for("subscriber.forgot_password"))
        # Generate password reset token
        token = binascii.hexlify(os.urandom(32)).decode()
        subscriber.password_reset_string = token
        database.session.commit()

        email_template = str(
            Path(
                current_app.root_path + "/emails/subscriber-reset-password.jinja2.html"
            )
        )
        company = Company.query.first()
        password_reset_url = (
            "https://" + flask.request.host + "/account/password-reset?token=" + token
        )

        with open(email_template) as file_:
            template = Template(file_.read())
            html = template.render(
                password_reset_url=password_reset_url, company=company
            )

            try:
                msg = EmailMessageQueue()
                msg["Subject"] = company.name + " " + "Password Reset"
                msg["FROM"] = current_app.config["EMAIL_LOGIN_FROM"]
                msg["TO"] = email
                msg.set_content(password_reset_url)
                msg.add_alternative(html, subtype="html")
                msg.queue()
            except Exception as e:
                log.error(f"Failed to send subscriber password reset email. {e}")
            flash(
                "We've sent you an email with a password reset link, \
                    please check your spam/junk folder too"
            )

    return render_template("subscriber/forgot_password.html", form=form)


@subscriber.route("/account/password-reset", methods=["GET", "POST"])
def password_reset():
    "Perform password reset from email link, verify token"
    form = SubscriberResetPasswordForm()

    if form.validate_on_submit():
        if (
            Person.query.filter_by(password_reset_string=form.data["token"]).first()
            is None
        ):
            return "Invalid reset token"

        person = Person.query.filter_by(
            password_reset_string=form.data["token"]
        ).first()
        person.set_password(form.data["password"])
        person.password_expired = False
        database.session.commit()
        flash("Your password has been reset")
        return redirect(url_for("subscriber.login", email=person.email))

    if (
        request.args.get("token", None) is None
        or len(request.args["token"]) != 64
        or Person.query.filter_by(password_reset_string=request.args["token"]).first()
        is None
    ):
        return "Invalid reset link. Please try generating a new reset link."

    return render_template(
        "subscriber/reset_password.html", token=request.args["token"], form=form
    )


@subscriber.route("/account")
@subscriber_login_required
def account():
    "A subscribers account home screen"
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()
    stripe_publishable_key = get_stripe_publishable_key()
    stripe_default_payment_method = None
    stripe_session = None
    failed_invoices = g.subscriber.failed_invoices()
    # Get subscribers first subscription to determine stripe customer id
    # excluding one-off plans.
    subscription = (
        database.session.query(Subscription)
        .execution_options(include_archived=True)
        .join(Person, Subscription.person_id == Person.id)
        .join(Plan, Subscription.sku_uuid == Plan.uuid)
        .join(PlanRequirements, Plan.id == PlanRequirements.plan_id)
        .where(Person.email == session["subscriber_id"])
        .where(PlanRequirements.subscription == 1)
        .order_by(Subscription.id.desc())
        .first()
    )
    if subscription:
        try:
            stripe_subscription = stripe.Subscription.retrieve(
                subscription.stripe_subscription_id,
                stripe_account=stripe_connect_account_id,
            )
            stripe_customer_id = stripe_subscription.customer
            stripe_customer = stripe.Customer.retrieve(
                stripe_customer_id, stripe_account=stripe_connect_account_id
            )

            stripe_session = stripe.checkout.Session.create(
                stripe_account=stripe_connect_account_id,
                payment_method_types=["card"],
                mode="setup",
                customer=stripe_customer_id,
                setup_intent_data={
                    "metadata": {
                        "subscription_id": stripe_subscription.id,
                    },
                },
                success_url=url_for("subscriber.account", _external=True)
                + "?stripe_session_id={CHECKOUT_SESSION_ID}",
                cancel_url=url_for("subscriber.account", _external=True),
            )
            if request.args.get("stripe_session_id"):
                # Process stripe update payment request
                # Get Stripe checkout session
                stripe_session = stripe.checkout.Session.retrieve(
                    request.args.get("stripe_session_id"),
                    stripe_account=stripe_connect_account_id,
                )
                # Get setup_intent id from stripe session
                stripe_setup_intent_id = stripe_session.setup_intent
                stripe_setup_intent = stripe.SetupIntent.retrieve(
                    stripe_setup_intent_id, stripe_account=stripe_connect_account_id
                )
                # Update default payment method
                stripe.Customer.modify(
                    stripe_customer.id,
                    stripe_account=stripe_connect_account_id,
                    invoice_settings={
                        "default_payment_method": stripe_setup_intent.payment_method
                    },
                )
                flash("Default payment method updated")
                return redirect(url_for("subscriber.account"))

            # Try to get existing default payment method
            if stripe_customer.invoice_settings.default_payment_method:
                stripe_default_payment_method = stripe.PaymentMethod.retrieve(
                    stripe_customer.invoice_settings.default_payment_method,
                    stripe_account=stripe_connect_account_id,
                )
        except stripe.error.InvalidRequestError as e:
            log.error(f"stripe.error.InvalidRequestError: {e}")
    return render_template(
        "subscriber/account.html",
        stripe_session=stripe_session,
        stripe_publishable_key=stripe_publishable_key,
        stripe_default_payment_method=stripe_default_payment_method,
        failed_invoices=failed_invoices,
    )


@subscriber.route("/account/subscriptions")
@subscriber_login_required
def subscriptions():
    "A subscribers subscriptions"
    return render_template("subscriber/subscriptions.html")


@subscriber.route(
    "/account/subscriptions/update-choices/<subscription_id>", methods=["GET", "POST"]
)
@subscriber_login_required
def update_subscription_choices(subscription_id):
    """Subscriber can update their subscription choices"""
    # Get plan from subscription
    subscription = Subscription.query.get(subscription_id)
    plan = subscription.plan
    if request.method == "POST":
        chosen_option_ids = []
        for choice_group_id in request.form.keys():
            for option_id in request.form.getlist(choice_group_id):
                chosen_option_ids.append(option_id)
        # Update chosen choices
        chosen_options = []
        for option_id in chosen_option_ids:
            option = Option.query.get(option_id)
            # Store as ChosenOption because option may change after order has processed
            # This preserves integrity of the actual chosen options
            chosen_option = ChosenOption()
            chosen_option.option_title = option.title
            chosen_option.choice_group_title = option.choice_group.title
            chosen_option.choice_group_id = (
                option.choice_group.id
            )  # Used for grouping latest choice
            chosen_options.append(chosen_option)
        subscription.chosen_options = chosen_options

        database.session.add(subscription)
        database.session.commit()
        flash("Your choices have been saved.")
        return redirect(url_for("subscriber.subscriptions"))
    else:
        return render_template("subscriber/update_choices.html", plan=plan)


@subscriber.route("/account/files")
@subscriber_login_required
def list_files():
    "View files"
    files = File.query.order_by(File.id.desc()).all()
    return render_template("subscriber/list_files.html", files=files)


@subscriber.route("/account/failed-invoices")
@subscriber_login_required
def subscriber_view_failed_invoices():
    """As a subscriber I can view my failed invoices
    (ref issue #805)
    A failed invoice means that all *automated* payment collection
    attemps for a given invoice has failed, **and** there wll be
    no further *automated* payment collections for this invoice.
    """
    failed_invoices = g.subscriber.failed_invoices()
    return render_template(
        "subscriber/subscriber_failed_invoices.html", failed_invoices=failed_invoices
    )


@subscriber.route("/account/pay-invoice")
@subscriber.route("/account/pay-invoice/<invoice_reference>")
@subscriber_login_required
def subscriber_pay_invoice(invoice_reference=None):
    """As a subscriber I can pay an invoice (including failed invoices)"""
    if invoice_reference is not None:
        # Try and get Stripe hosted url invoice payment page
        try:
            stripe.api_key = get_stripe_secret_key()
            stripe_connect_account_id = get_stripe_connect_account_id()
            invoice = stripe.Invoice.retrieve(
                invoice_reference, stripe_account=stripe_connect_account_id
            )
            return redirect(invoice.hosted_invoice_url)
        except Exception as e:
            log.error(
                "Subscriber tried byt unable to complete pay-invoice due to error {e}. Invoice reference: {invoice_reference}"
            )
    flash("No payment reference was given")
    return redirect(url_for("subscriber.subscriber_view_failed_invoices"))
