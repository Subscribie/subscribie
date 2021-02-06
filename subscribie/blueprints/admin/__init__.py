import logging
import json
from subscribie.database import database  # noqa
from flask import (
    Blueprint,
    render_template,
    flash,
    send_from_directory,
    current_app,
    redirect,
    url_for,
    jsonify,
    request,
    session,
    Response,
)
import jinja2
import requests
from jinja2 import Environment
from subscribie.utils import (
    get_stripe_secret_key,
    get_stripe_connect_account,
    create_stripe_connect_account,
    get_stripe_connect_account_id,
    modify_stripe_account_capability,
)
from subscribie.forms import (
    TawkConnectForm,
    ChangePasswordForm,
    GoogleTagManagerConnectForm,
    PlansForm,
    ChangeEmailForm,
    AddShopAdminForm,
    UploadLogoForm,
    WelcomeEmailTemplateForm,
    SetReplyToEmailForm,
    UploadFilesForm,
)
from subscribie.auth import login_required, protected_download
from flask_uploads import UploadSet, IMAGES
import os
from pathlib import Path
from .getLoadedModules import getLoadedModules
import uuid
from sqlalchemy import desc
from datetime import datetime
from subscribie.models import (
    Transaction,
    EmailTemplate,
    Setting,
    File,
    User,
    Person,
    Subscription,
    Company,
    Integration,
    PaymentProvider,
    Plan,
    PlanRequirements,
    PlanSellingPoints,
)
import stripe
from werkzeug.utils import secure_filename


admin = Blueprint(
    "admin", __name__, template_folder="templates", static_folder="static"
)

from .ResetSite import remove_subscriptions  # noqa: F401,E402
from .choice_group import list_choice_groups  # noqa: F401, E402
from .option import list_options  # noqa: F401, E402
from .subscriber import show_subscriber  # noqa: F401, E402
from .export_subscribers import export_subscribers  # noqa: F401, E402a


def dec2pence(amount):
    """Take two decimal place string and convert to pence"""
    if amount == "":
        return 0
    import math

    return int(math.ceil(float(amount) * 100))


@admin.app_template_filter()
def currencyFormat(value):
    value = float(value) / 100
    return "£{:,.2f}".format(value)


def store_stripe_transaction(stripe_external_id):
    """Store Stripe invoice payment in transactions table"""
    stripe.api_key = get_stripe_secret_key()
    stripe_connect_account_id = get_stripe_connect_account_id()

    invoice = None

    # It might be an upcoming invoice or an existing invoice which
    # is being updated
    # First try fetching paid invoice
    try:
        invoice = stripe.Invoice.retrieve(
            id=stripe_external_id,
            stripe_account=stripe_connect_account_id,
        )
    except stripe.error.InvalidRequestError as e:
        print(f"Cannot get stripe invoice subscription id: {stripe_external_id}")
        print("This might be okay. Trying to fetch upcoming invoice with same id...")
        print(e)
        try:
            invoice = stripe.Invoice.upcoming(
                subscription=stripe_external_id,
                stripe_account=stripe_connect_account_id,
            )
        except stripe.error.InvalidRequestError as e:
            print(
                f"Cannot get stripe upcoming invoice subscription id: \
                  {stripe_external_id}"
            )
            print(e)
            raise Exception(
                f"Cannot locate Stripe subscription invoice {stripe_external_id}"
            )

    # Check if there's an existing payment record in transactions table
    transaction = Transaction.query.filter_by(external_id=stripe_external_id).first()
    if transaction is None:
        # No existing transaction found, so add payment info from Stripe invoice
        # Note, if the subscription invoice is unsettled, its amount could
        # potentially change until it's finalized

        # Store as transaction
        transaction = Transaction()
        transaction.amount = invoice.amount_due
        transaction.payment_status = invoice.status
        transaction.comment = str(invoice.lines.data[0].metadata)
        transaction.external_id = stripe_external_id
        transaction.external_src = "stripe"
        # Find related subscribie subscription model if exists
        subscription = Subscription.query.filter_by(
            stripe_external_id=stripe_external_id
        ).first()
        if subscription is not None:
            transaction.subscription = subscription
        try:
            transaction.person = subscription.person
        except AttributeError:  # A transaction may not have a person
            pass

    # Update payment_status to stripe latest status
    transaction.payment_status = invoice.status

    database.session.add(transaction)
    database.session.commit()  # Save/update transaction in transactions table
    return transaction


@admin.route("payments/update/<stripe_external_id>")
@login_required
def update_payment_fulfillment(stripe_external_id):
    """Update payment fulfillment stage"""

    transaction = Transaction.query.filter_by(external_id=stripe_external_id).first()
    if transaction is None:
        transaction = store_stripe_transaction(stripe_external_id)

    # Update transactions fulfillment_state to the value specified
    fulfillment_state = request.args.get("state", "")
    # Check a valid fulfillment_state is passed (only one or empty at the moment)
    if fulfillment_state == "" or fulfillment_state == "complete":
        transaction.fulfillment_state = fulfillment_state
        flash("Fulfillment state updated")

    database.session.add(transaction)
    database.session.commit()  # Save/update transaction in transactions table

    # Go back to previous page
    return redirect(request.referrer)


@admin.route("/stripe/subscriptions/<subscription_id>/actions/pause")
@login_required
def pause_stripe_subscription(subscription_id: str):
    """Pause a Stripe subscription"""
    stripe.api_key = get_stripe_secret_key()
    connect_account_id = get_stripe_connect_account_id()

    try:
        stripe.Subscription.modify(
            subscription_id,
            stripe_account=connect_account_id,
            pause_collection={"behavior": "void"},
        )
        flash("Subscription paused")
    except Exception as e:
        flash("Error pausing subscription")
        print(e)

    if "goback" in request.args:
        return redirect(request.referrer)
    return jsonify(message="Subscription paused", subscription_id=subscription_id)


@admin.route("/stripe/subscriptions/<subscription_id>/actions/resume")
@login_required
def resume_stripe_subscription(subscription_id):
    """Resume a Stripe subscription"""
    stripe.api_key = get_stripe_secret_key()
    connect_account_id = get_stripe_connect_account_id()

    try:
        stripe.Subscription.modify(
            subscription_id,
            stripe_account=connect_account_id,
            pause_collection="",  # passing empty string unpauses the subscription
        )
        flash("Subscription resumed")
    except Exception as e:
        flash("Error resuming subscription")
        print(e)

    if "goback" in request.args:
        return redirect(request.referrer)

    return jsonify(message="Subscription resumed", subscription_id=subscription_id)


@admin.route("/dashboard")
@login_required
def dashboard():
    integration = Integration.query.first()
    payment_provider = PaymentProvider.query.first()
    if payment_provider is None:
        # If payment provider table is not seeded, seed it now with blank values.
        payment_provider = PaymentProvider()
        database.session.add(payment_provider)
        database.session.commit()
    if payment_provider.stripe_active:
        stripe_connected = True
    else:
        stripe_connected = False
    return render_template(
        "admin/dashboard.html",
        stripe_connected=stripe_connected,
        integration=integration,
        loadedModules=getLoadedModules(),
    )


@admin.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    """Edit plans

    Note plans are immutable, when a change is made to plan, its old
    plan is archived and a new plan is created with a new uuid. This is to
    protect data integriry and make sure plan history is retained, via its uuid.
    If a user needs to change a subscription, they should change to a different
    plan with a different uuid.

    """

    form = PlansForm()
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    if form.validate_on_submit():
        company = Company.query.first()
        company.name = request.form["company_name"]
        company.slogan = request.form["slogan"]
        # Loop plans
        for index in request.form.getlist("planIndex", type=int):

            # Archive existing plan then create new plan
            # (remember, edits create new plans because
            # plans are immutable)
            plan = Plan.query.filter_by(uuid=form.uuid.data[index]).first()
            plan.archived = True

            # Build new plan
            draftPlan = Plan()
            database.session.add(draftPlan)
            plan_requirements = PlanRequirements()

            draftPlan.uuid = str(uuid.uuid4())
            draftPlan.requirements = plan_requirements
            # Preserve primary icon if exists
            draftPlan.primary_icon = plan.primary_icon

            # Preserve choice_groups
            draftPlan.choice_groups = plan.choice_groups

            draftPlan.title = getPlan(form.title.data, index, default="").strip()

            draftPlan.position = getPlan(form.position.data, index)
            if getPlan(form.description.data, index) != "":
                draftPlan.description = getPlan(form.description.data, index)

            if getPlan(form.subscription.data, index) == "yes":
                plan_requirements.subscription = True
            else:
                plan_requirements.subscription = False

            interval_unit = getPlan(form.interval_unit.data, index, default="")
            if (
                "monthly" in interval_unit
                or "yearly" in interval_unit
                or "weekly" in interval_unit
            ):
                draftPlan.interval_unit = interval_unit

            if getPlan(form.interval_amount.data, index, default=0) is None:
                interval_amount = 0
            else:
                interval_amount = dec2pence(
                    getPlan(form.interval_amount.data, index, default=0)
                )
            draftPlan.interval_amount = interval_amount
            if getPlan(form.instant_payment.data, index) == "yes":
                plan_requirements.instant_payment = True
            else:
                plan_requirements.instant_payment = False

            if getPlan(form.note_to_seller_required.data, index) == "yes":
                plan_requirements.note_to_seller_required = True
            else:
                plan_requirements.note_to_seller_required = False

            plan_requirements.note_to_buyer_message = str(
                getPlan(form.note_to_buyer_message, index, default="").data
            )

            try:
                days_before_first_charge = int(
                    form.days_before_first_charge[index].data
                )
            except ValueError:
                days_before_first_charge = 0

            draftPlan.days_before_first_charge = days_before_first_charge

            if getPlan(form.sell_price.data, index, default=0) is None:
                sell_price = 0
            else:
                sell_price = dec2pence(getPlan(form.sell_price.data, index, default=0))

            draftPlan.sell_price = sell_price

            points = getPlan(form.selling_points.data, index, default="")
            for point in points:
                draftPlan.selling_points.append(PlanSellingPoints(point=point))

            # Primary icon image storage
            f = getPlan(form.image.data, index)
            if f:
                images = UploadSet("images", IMAGES)
                filename = images.save(f)
                src = url_for("views.custom_static", filename=filename)
                draftPlan.primary_icon = src
        database.session.commit()  # Save
        flash("Plan(s) updated.")
        return redirect(request.referrer)
    return render_template("admin/edit.html", plans=plans, form=form)


@admin.route("/add", methods=["GET", "POST"])
@login_required
def add_plan():
    form = PlansForm()
    if form.validate_on_submit():
        draftPlan = Plan()
        database.session.add(draftPlan)
        plan_requirements = PlanRequirements()
        draftPlan.requirements = plan_requirements

        draftPlan.uuid = str(uuid.uuid4())
        draftPlan.title = form.title.data[0].strip()
        draftPlan.position = request.form.get("position-0", 0)
        interval_unit = form.interval_unit.data[0].strip()

        if form.description.data[0].strip() != "":
            draftPlan.description = form.description.data[0]
        if (
            "monthly" in interval_unit
            or "yearly" in interval_unit
            or "weekly" in interval_unit
        ):
            draftPlan.interval_unit = interval_unit

        if form.subscription.data[0] == "yes":
            plan_requirements.subscription = True
        else:
            plan_requirements.subscription = False
        if form.note_to_seller_required.data[0] == "yes":
            plan_requirements.note_to_seller_required = True
        else:
            plan_requirements.note_to_seller_required = False

        plan_requirements.note_to_buyer_message = str(
            form.note_to_buyer_message.data[0]
        )
        try:
            days_before_first_charge = int(form.days_before_first_charge.data[0])
        except ValueError:
            days_before_first_charge = 0

        draftPlan.days_before_first_charge = days_before_first_charge

        if form.interval_amount.data[0] is None:
            draftPlan.interval_amount = 0
        else:
            draftPlan.interval_amount = dec2pence(form.interval_amount.data[0])

        if form.instant_payment.data[0] == "yes":
            plan_requirements.instant_payment = True
        else:
            plan_requirements.instant_payment = False

        if form.sell_price.data[0] is None:
            draftPlan.sell_price = 0
        else:
            draftPlan.sell_price = dec2pence(form.sell_price.data[0])

        points = form.selling_points.data[0]

        for point in points:
            draftPlan.selling_points.append(PlanSellingPoints(point=point))

        # Primary icon image storage
        f = form.image.data[0]
        if f:
            images = UploadSet("images", IMAGES)
            filename = images.save(f)
            src = url_for("views.custom_static", filename=filename)
            draftPlan.primary_icon = src

        database.session.commit()
        flash("Plan added.")
        return redirect(url_for("admin.dashboard"))
    return render_template("admin/add_plan.html", form=form)


@admin.route("/delete", methods=["GET"])
@login_required
def delete_plan():
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    return render_template("admin/delete_plan_choose.html", plans=plans)


@admin.route("/delete/<uuid>", methods=["GET", "POST"])
@login_required
def delete_plan_by_uuid(uuid):
    """Archive (dont actually delete) an plan"""
    plan = Plan.query.filter_by(uuid=uuid).first()

    if "confirm" in request.args:
        return render_template(
            "admin/delete_plan_choose.html", confirm=False, plan=plan
        )
    if uuid is not False:
        # Perform archive
        plan.archived = True
        database.session.commit()

    flash("Plan deleted.")
    plans = Plan.query.filter_by(archived=0).all()
    return render_template("admin/delete_plan_choose.html", plans=plans)


@admin.route("/connect/stripe-set-livemode", methods=["POST"])
@login_required
def set_stripe_livemode():
    livemode = request.data.decode("utf-8")
    if livemode == "0" or livemode == "1":
        payment_provider = PaymentProvider.query.first()
        payment_provider.stripe_livemode = int(livemode)
        database.session.commit()
        return redirect("/admin/connect/stripe-connect")

    return jsonify("Invalid request, valid values: 'live' or 'test'"), 500


@admin.route("/connect/stripe-connect", methods=["GET"])
@login_required
def stripe_connect():
    account = None
    stripe_express_dashboard_url = None
    stripe.api_key = get_stripe_secret_key()
    payment_provider = PaymentProvider.query.first()

    try:
        account = get_stripe_connect_account()
        if account is not None and account.charges_enabled and account.payouts_enabled:
            payment_provider.stripe_active = True
        else:
            payment_provider.stripe_active = False
    except (
        stripe.error.PermissionError,
        stripe.error.InvalidRequestError,
        AttributeError,
    ) as e:
        print(e)
        account = None

    # Setup Stripe webhook endpoint if it dosent already exist
    if account:
        # Attempt to Updates an existing Account Capability to accept card payments
        try:
            account = get_stripe_connect_account()
            modify_stripe_account_capability(account.id)
        except Exception as e:
            logging.info("Could not update card_payments capability for account")
            logging.info(e)

        try:
            stripe_express_dashboard_url = stripe.Account.create_login_link(
                account.id
            ).url
        except stripe.error.InvalidRequestError:
            stripe_express_dashboard_url = None

    database.session.commit()
    return render_template(
        "admin/settings/stripe/stripe_connect.html",
        stripe_onboard_path=url_for("admin.stripe_onboarding"),
        account=account,
        payment_provider=payment_provider,
        stripe_express_dashboard_url=stripe_express_dashboard_url,
    )


@admin.route("/stripe-onboard", methods=["POST"])
@login_required
def stripe_onboarding():
    # Determine if in live or test mode
    payment_provider = PaymentProvider.query.first()
    stripe.api_key = get_stripe_secret_key()

    company = Company.query.first()

    # Use existing stripe_connect_account_id, otherwise create stripe connect account
    try:
        print("Trying if there's an existing stripe account")
        account = get_stripe_connect_account()
        print(f"Yes, stripe account found: {account.id}")
    except (
        stripe.error.PermissionError,
        stripe.error.InvalidRequestError,
        AttributeError,
    ):
        print("Could not find a stripe account, Creating stripe account")
        account = create_stripe_connect_account(company)
        if payment_provider.stripe_livemode:
            payment_provider.stripe_live_connect_account_id = account.id
        else:
            payment_provider.stripe_test_connect_account_id = account.id

    database.session.commit()

    session["account_id"] = account.id
    account_link_url = _generate_account_link(account.id)
    try:
        return jsonify({"url": account_link_url})
    except Exception as e:
        return jsonify(error=str(e)), 403


def _generate_account_link(account_id):
    """
    From the Stripe Docs:
    A user that is redirected to your return_url might not have completed the
    onboarding process. Use the /v1/accounts endpoint to retrieve the user’s
    account and check for charges_enabled. If the account is not fully onboarded,
    provide UI prompts to allow the user to continue onboarding later. The user
    can complete their account activation through a new account link (generated
    by your integration). You can check the state of the details_submitted
    parameter on their account to see if they’ve completed the onboarding process.
    """
    account_link = stripe.AccountLink.create(
        type="account_onboarding",
        account=account_id,
        refresh_url=url_for("admin.stripe_connect", refresh="refresh", _external=True),
        return_url=url_for("admin.stripe_connect", success="success", _external=True),
    )
    return account_link.url


@admin.route("/stripe-onboard/refresh", methods=["GET"])
def onboard_user_refresh():
    if "account_id" not in session:
        return redirect(url_for("admin.stripe_onboarding"))

    account_id = session["account_id"]

    account_link_url = _generate_account_link(account_id)
    return redirect(account_link_url)


@admin.route("/connect/google_tag_manager/manually", methods=["GET", "POST"])
@login_required
def connect_google_tag_manager_manually():
    integration = Integration.query.first()
    form = GoogleTagManagerConnectForm()
    if form.validate_on_submit():
        container_id = form.data["container_id"]
        integration.google_tag_manager_container_id = container_id
        integration.google_tag_manager_active = True
        database.session.commit()
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_google_tag_manager_manually.html",
            form=form,
            integration=integration,
        )


@admin.route("/connect/tawk/manually", methods=["GET", "POST"])
@login_required
def connect_tawk_manually():
    integration = Integration.query.first()
    form = TawkConnectForm()
    if form.validate_on_submit():
        property_id = form.data["property_id"]
        integration.tawk_property_id = property_id
        integration.tawk_active = True
        database.session.commit()
        return redirect(url_for("admin.dashboard"))
    else:
        return render_template(
            "admin/connect_tawk_manually.html", form=form, integration=integration
        )


@admin.context_processor
def utility_get_transaction_fulfillment_state():
    """return fulfullment_state of transaction"""

    def get_transaction_fulfillment_state(external_id):
        transaction = Transaction.query.filter_by(external_id=external_id).first()
        if transaction:
            return transaction.fulfillment_state
        else:
            return None

    return dict(get_transaction_fulfillment_state=get_transaction_fulfillment_state)


def get_subscription_status(stripe_external_id: str) -> str:
    status_on_error = "Unknown"
    if stripe_external_id is None:
        return status_on_error
    try:
        stripe.api_key = get_stripe_secret_key()
        connect_account = get_stripe_connect_account()
        subscription = stripe.Subscription.retrieve(
            stripe_account=connect_account.id, id=stripe_external_id
        )
        if subscription.pause_collection is not None:
            return "paused"
        else:
            return "active"
    except stripe.error.InvalidRequestError as e:
        print(e)
        return status_on_error
    except ValueError as e:
        print(e)
        return status_on_error


@admin.context_processor
def subscription_status():
    def formatted_status(stripe_external_id):
        return (
            get_subscription_status(stripe_external_id).capitalize().replace("_", " ")
        )

    return dict(subscription_status=formatted_status)


@admin.route("/subscribers")
@login_required
def subscribers():
    page = request.args.get("page", 1, type=int)
    action = request.args.get("action")

    show_active = action == "show_active"

    def url_pagination(page=None):
        return url_for("admin.subscribers", page=page, action=action)

    query = database.session.query(Person).order_by(desc(Person.created_at))

    if show_active:
        query = query.filter(Person.subscriptions.any())

    people = query.paginate(page=page, per_page=2)

    return render_template(
        "admin/subscribers.html",
        people=people,
        url_pagination=url_pagination,
        show_active=show_active,
    )


@admin.route("/upcoming-invoices")
@login_required
def upcoming_invoices():
    get_stripe_secret_key()
    all_subscriptions = Subscription.query.all()
    subscriptions = []
    for subscription in all_subscriptions:
        if subscription.upcoming_invoice() is not None:
            subscriptions.append(subscription)

    return render_template(
        "admin/upcoming_invoices.html",
        subscriptions=subscriptions,
        datetime=datetime,
    )


@admin.route("/invoices")
@login_required
def invoices():
    stripe.api_key = get_stripe_secret_key()
    connect_account = get_stripe_connect_account()
    invoices = stripe.Invoice.list(stripe_account=connect_account.id)

    return render_template(
        "admin/invoices.html",
        invoices=invoices,
        datetime=datetime,
    )


@admin.route("/transactions", methods=["GET"])
@login_required
def transactions():

    page = request.args.get("page", 1, type=int)
    transactions = (
        database.session.query(Transaction)
        .order_by(desc(Transaction.created_at))
        .paginate(page=page, per_page=10)
    )

    return render_template("admin/transactions.html", transactions=transactions)


@admin.route("/order-notes", methods=["GET"])
@login_required
def order_notes():
    """Notes to seller given during subscription creation"""
    subscriptions = Subscription.query.order_by(desc("created_at")).all()
    return render_template("admin/order-notes.html", subscriptions=subscriptions)


@admin.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password of existing user"""
    form = ChangePasswordForm()
    if request.method == "POST":
        email = session.get("user_id", None)
        if email is None:
            return "Email not found in session"

        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            if user is None:
                return "User not found with that email"
            else:
                user.set_password(request.form["password"])
                database.session.commit()
            flash("Password has been updated")
        else:
            return "Invalid password form submission"
        return redirect(url_for("admin.change_password"))
    else:
        return render_template("admin/change_password.html", form=form)


@admin.route("/change-email", methods=["GET", "POST"])
@login_required
def change_email():
    """Change email of existing user"""
    form = ChangeEmailForm()
    if request.method == "POST":
        email = session.get("user_id", None)
        if email is None:
            return "Email not found in session"

        if form.validate_on_submit():
            user = User.query.filter_by(email=email).first()
            if user is None:
                return "User not found with that email"
            else:
                new_email = request.form["email"]
                user.email = new_email
                database.session.commit()
            flash(f"Email has been updated to {new_email}. Please re-login")
        else:
            return "Invalid email form submission"
        return redirect(url_for("admin.change_email"))
    else:
        return render_template("admin/change_email.html", form=form)


@admin.route("/add-shop-admin", methods=["GET", "POST"])
@login_required
def add_shop_admin():
    """Add another shop admin"""
    form = AddShopAdminForm()
    if request.method == "POST":

        if form.validate_on_submit():
            # Check user dosent already exist
            email = request.form["email"]
            if User.query.filter_by(email=email).first() is not None:
                return f"Error, admin with email ({email}) already exists."

            user = User()
            user.email = email
            user.set_password(request.form["password"])
            database.session.add(user)
            database.session.commit()
            flash(f"A new shop admin with email {email} has been added")
        else:
            return "Invalid add shop admin form submission"
        return redirect(url_for("admin.add_shop_admin"))
    else:
        return render_template("admin/add_shop_admin.html", form=form)


@admin.route("/upload-logo", methods=["GET", "POST"])
@login_required
def upload_logo():
    """Upload shop logo"""
    form = UploadLogoForm()
    company = Company.query.first()

    if form.validate_on_submit():
        images = UploadSet("images", IMAGES)
        f = form.image.data
        if f is None:
            flash("File required")
        else:
            filename = images.save(f)
            src = url_for("views.custom_static", filename=filename)
            company.logo_src = src
            database.session.commit()
            flash("Logo has been uploaded")

    return render_template("admin/upload_logo.html", form=form, company=company)


@admin.route("/remove-logo", methods=["GET"])
@login_required
def remove_logo():
    """Remove logo from shop"""
    company = Company.query.first()
    company.logo_src = None
    database.session.commit()
    flash("Logo removed")
    # Return user to previous page
    return redirect(request.referrer)


@admin.route("/remove-plan-image/<plan_id>", methods=["GET"])
@login_required
def remove_plan_image(plan_id):
    """Remove primary image from plan"""
    plan = Plan.query.get(plan_id)
    plan.primary_icon = None
    database.session.commit()
    flash("Plan image removed")
    # Return user to previous page
    return redirect(request.referrer)


@admin.route("/welcome-email-edit", methods=["GET", "POST"])
@login_required
def edit_welcome_email():
    """Edit welcome email template"""
    company = Company.query.first()
    form = WelcomeEmailTemplateForm()
    default_template = open(
        Path(current_app.root_path + "/emails/welcome.jinja2.html")
    ).read()
    custom_template = EmailTemplate.query.first()
    new_custom_template = None

    if request.method == "POST":
        new_custom_template = form.template.data

    if custom_template is None:  # First time creating custom template
        custom_template = EmailTemplate()
        database.session.add(custom_template)

    if form.validate_on_submit() and form.use_custom_welcome_email.data is True:

        new_custom_template = form.template.data
        # Validate template syntax
        env = Environment()
        try:
            env.parse(new_custom_template)
            # Store the validated template
            custom_template.custom_welcome_email_template = new_custom_template
            custom_template.use_custom_welcome_email = True
            flash("Email template has been saved.")
            flash("Using custom template for welcome email")
        except jinja2.exceptions.TemplateSyntaxError as e:
            form.template.errors.append(e)

    else:
        custom_template.use_custom_welcome_email = False
        if request.method == "POST":
            flash("Using default template for welcome email")

    database.session.commit()

    return render_template(
        "admin/email/edit_customer_sign_up_email.html",
        form=form,
        default_template=default_template,
        custom_template=custom_template.custom_welcome_email_template,
        new_custom_template=new_custom_template,
        use_custom_welcome_email=custom_template.use_custom_welcome_email,
        company=company,
    )


@admin.route("/set-reply-to-email", methods=["GET", "POST"])
@login_required
def set_reply_to_email():
    """Set reply-to email"""
    form = SetReplyToEmailForm()
    setting = Setting.query.first()
    if setting is None:
        setting = Setting()
        database.session.add(setting)

    current_email = setting.reply_to_email_address

    if form.validate_on_submit():
        email = form.email.data
        setting.reply_to_email_address = email
        database.session.commit()
        flash(f"Reply-to email address set to: {email}")
    return render_template(
        "admin/settings/set_reply_to_email.html", form=form, current_email=current_email
    )


@admin.route("/announce-stripe-connect", methods=["GET"])
def announce_shop_stripe_connect_ids():
    """Accounce this shop's stripe connect account id(s)
    to the STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST
    - stripe_live_connect_account_id
    - stripe_test_connect_account_id
    The single stripe webhook endpoint needs to know
    which shops to send events to. Do this this, it needs
    to know the stripe_live_connect_account_id and
    stripe_test_connect_account_id on the payment_provider
    model, as well as the shop address (flask.request.host_url).

    This endpoint (announce_shop_stripe_connect_ids) is called
    via cron for each shop to keep the connect_account_id
    up to date should they change. It can also be called manually.
    It does not matter how many times this is called.
    """
    stripe_live_connect_account_id = None
    stripe_test_connect_account_id = None
    msg = None
    ANNOUNCE_HOST = current_app.config["STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST"]

    payment_provider = PaymentProvider.query.first()

    def announce_stripe_connect_account(account_id, live_mode=0):
        logging.debug(
            f"Announcing stripe account to {url_for('index', _external=True)}"
        )
        requests.post(
            ANNOUNCE_HOST,
            json={
                "stripe_connect_account_id": account_id,
                "live_mode": live_mode,
                "site_url": url_for("index", _external=True),
            },
        )

    try:
        if payment_provider.stripe_live_connect_account_id is not None:
            stripe_live_connect_account_id = (
                payment_provider.stripe_live_connect_account_id
            )
            announce_stripe_connect_account(stripe_live_connect_account_id, live_mode=1)

        if payment_provider.stripe_test_connect_account_id is not None:
            # send test connect account id
            stripe_test_connect_account_id = (
                payment_provider.stripe_test_connect_account_id
            )
            announce_stripe_connect_account(stripe_test_connect_account_id, live_mode=0)

        stripe_connect_account_id = None
        if stripe_live_connect_account_id is not None:
            stripe_connect_account_id = stripe_test_connect_account_id
        elif stripe_test_connect_account_id is not None:
            stripe_connect_account_id = stripe_test_connect_account_id

        msg = {
            "msg": f"Announced Stripe connect account {stripe_connect_account_id} \
for site_url {request.host_url}, to the STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST: \
{current_app.config['STRIPE_CONNECT_ACCOUNT_ANNOUNCER_HOST']}\n\
WARNING: Check logs to verify recipt"
        }
        logging.info(msg)
    except Exception as e:
        msg = f"Failed to announce stripe connect id:\n{e}"
        logging.error(msg)

    return Response(json.dumps(msg), status=200, mimetype="application/json")


@admin.route("/upload-files", methods=["GET", "POST"])
@login_required
def upload_files():
    """Upload files to shop"""
    form = UploadFilesForm()
    allowed = [
        "image/png",
        "image/gif",
        "image/jpg",
        "image/jpeg",
        "audio/mpeg",
        "video/mpeg",
        "audio/ogg",
        "video/ogg",
        "application/ogg",
        "application/pdf",
        "application/vnd.ms-powerpoint",
        "application/vnd.ms-excel",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ]
    if form.validate_on_submit():
        for upload in request.files.getlist("upload"):
            # Check filetype
            if upload.content_type in allowed:
                filename = secure_filename(upload.filename)
                # Store to filesystem
                upload.save(
                    dst=current_app.config["UPLOADED_FILES_DEST"] + "/" + filename
                )
                # Store file meta in db
                uploadedFile = File()
                uploadedFile.file_name = filename
                database.session.add(uploadedFile)
                flash(f"Uploaded {filename}")
        database.session.commit()
    return render_template("admin/uploads/upload_files.html", form=form)


@admin.route("/list-files", methods=["GET"])
@login_required
def list_files():
    files = File.query.all()
    return render_template("admin/uploads/list_files.html", files=files)


@admin.route("/delete/file/<uuid>")
@login_required
def delete_file(uuid):
    # Remove from database file meta
    theFile = File.query.filter_by(uuid=uuid).first()
    if theFile is not None:
        database.session.delete(theFile)

    database.session.commit()
    # Remove from filesystem
    try:
        os.unlink(current_app.config["UPLOADED_FILES_DEST"] + theFile.file_name)
    except Exception as e:
        print(e)
    flash(f"Deleted: {theFile.file_name}")
    return redirect(request.referrer)


@admin.route("/uploads/<uuid>")
@protected_download
def download_file(uuid):
    theFile = File.query.filter_by(uuid=uuid).first()
    if theFile is not None:
        return send_from_directory(
            current_app.config["UPLOADED_FILES_DEST"],
            theFile.file_name,
            as_attachment=True,
        )
    else:
        return "Not found", 404


def getPlan(container, i, default=None):
    try:
        return container[i]
    except IndexError:
        return default
