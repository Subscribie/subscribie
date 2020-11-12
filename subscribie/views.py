import os
import logging
from uuid import uuid4
from .signals import journey_complete
from subscribie.forms import CustomerForm
from subscribie.utils import (
    get_stripe_publishable_key,
    get_stripe_secret_key,
    get_stripe_connect_account,
    create_stripe_webhook,
    format_to_stripe_interval,
)
from subscribie.auth import check_private_page
import stripe
from pathlib import Path
import jinja2
from jinja2 import Template, Environment, FileSystemLoader


from flask import (
    abort,
    Blueprint,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
    jsonify,
    current_app,
    g,
)
import flask

from .models import (
    User,
    Person,
    Subscription,
    SubscriptionNote,
    Company,
    Plan,
    Integration,
    PaymentProvider,
    Transaction,
    Page,
    Option,
    ChosenOption,
    EmailTemplate,
    Setting,
)

from .database import database

from flask_mail import Mail, Message
import json

bp = Blueprint("views", __name__, url_prefix=None)


@bp.before_app_request
def check_if_inside_iframe():
    """Set iframe_embeded in session object if app is loaded from inside an iframe
    If visited directly, (e.g. as a shop admin),
    then referer header is emtpy, and therefore the header/footer is
    displayed as normal.
    """
    if (
        request.args.get("iframe_embeded", False)
        or session.get("iframe_embeded") is True
        and request.headers.get("referer") is not None
    ):
        print("Loading from within iframe")
        session["iframe_embeded"] = True
    else:
        session["iframe_embeded"] = False


@bp.app_context_processor
def inject_template_globals():
    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    return dict(company=company, integration=integration, plans=plans, pages=pages)


def redirect_url():
    return request.args.get("next") or request.referrer or url_for("index")


def index():
    return render_template("index.html")


@bp.route("/500")
def show_500():
    """Force 500 error"""
    return abort(500)


@bp.route("/choose")
def choose():
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    return render_template("choose.html", plans=plans)


def redirect_to_payment_step(plan, inside_iframe=False):
    """Depending on plans payment requirement, redirect to collection page
    accordingly"""

    scheme = "https" if request.is_secure else "http"

    return redirect(url_for("views.up_front", _scheme=scheme, _external=True))


@bp.route("/new_customer", methods=["GET"])
def new_customer():
    plan = Plan.query.filter_by(uuid=request.args["plan"]).first()
    session["plan"] = plan.uuid

    # Fetch selected options, if present
    chosen_options = []
    if session.get("chosen_option_ids", None):
        for option_id in session["chosen_option_ids"]:
            option = Option.query.get(option_id)
            # We will store as ChosenOption because option may change after the order
            # has processed. This preserves integrity of the actual chosen options
            chosen_option = ChosenOption()
            chosen_option.option_title = option.title
            chosen_option.choice_group_title = option.choice_group.title
            chosen_options.append(chosen_option)

    package = request.args.get("plan", "not set")
    session["package"] = package
    plan = Plan.query.filter_by(uuid=request.args.get("plan")).first()
    form = CustomerForm()
    return render_template(
        "new_customer.html",
        form=form,
        package=package,
        plan=plan,
        chosen_options=chosen_options,
    )


@bp.route("/new_customer", methods=["POST"])
def store_customer():
    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    form = CustomerForm()
    if form.validate():
        given_name = form.data["given_name"]
        family_name = form.data["family_name"]
        address_line_one = form.data["address_line_one"]
        city = form.data["city"]
        postcode = form.data["postcode"]
        email = form.data["email"]
        mobile = form.data["mobile"]
        # Store customer in session
        sid = session["sid"]
        # Store email in session
        session["email"] = email
        session["given_name"] = given_name

        # Store person info in session for form pre-population
        session["given_name"] = given_name
        session["family_name"] = family_name
        session["address_line_one"] = address_line_one
        session["city"] = city
        session["postcode"] = postcode
        session["email"] = email
        session["mobile"] = mobile

        # Don't store person if already exists
        person = Person.query.filter_by(email=email).first()
        if person is None:
            # Store person, with randomly generated password
            person = Person(
                sid=sid,
                given_name=given_name,
                family_name=family_name,
                address_line1=address_line_one,
                city=city,
                postal_code=postcode,
                email=email,
                mobile=mobile,
                password=str(os.urandom(16)),
            )
            database.session.add(person)
            database.session.commit()
        session["person_id"] = person.id
        # Store note to seller in session if there is one
        note_to_seller = form.data["note_to_seller"]
        session["note_to_seller"] = note_to_seller

        if form.data["is_iframe"] == "True":
            inside_iframe = True
        else:
            inside_iframe = False
        return redirect_to_payment_step(plan, inside_iframe=inside_iframe)
    else:
        return "There was an error processing that form, please go back and try again."


@bp.route("/set_options/<plan_uuid>", methods=["GET", "POST"])
def set_options(plan_uuid):
    plan = Plan.query.filter_by(uuid=plan_uuid).first()

    if request.method == "POST":
        # Store chosen options in session
        session["chosen_option_ids"] = []
        for choice_group_id in request.form.keys():
            for option_id in request.form.getlist(choice_group_id):
                session["chosen_option_ids"].append(option_id)

        return redirect(url_for("views.new_customer", plan=plan_uuid))

    return render_template("set_options.html", plan=plan)


@bp.route("/up_front", methods=["GET"])
def up_front():
    payment_provider = PaymentProvider.query.first()
    if (
        payment_provider.stripe_livemode
        and payment_provider.stripe_live_connect_account_id is None
        or payment_provider.stripe_livemode is False
        and payment_provider.stripe_test_connect_account_id is None
    ):

        return """Shop owner has not connected Stripe payments yet.
                This can be done by the shop owner via the admin dashboard."""

    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    stripe_pub_key = get_stripe_publishable_key()
    company = Company.query.first()
    stripe_create_checkout_session_url = url_for("views.stripe_create_checkout_session")

    if payment_provider.stripe_livemode:
        stripe_connected_account_id = payment_provider.stripe_live_connect_account_id
    else:
        stripe_connected_account_id = payment_provider.stripe_test_connect_account_id

    return render_template(
        "up_front_payment.html",
        company=company,
        plan=plan,
        fname=session["given_name"],
        stripe_pub_key=stripe_pub_key,
        stripe_create_checkout_session_url=stripe_create_checkout_session_url,
        stripe_connected_account_id=stripe_connected_account_id,
    )


@bp.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    payment_provider = PaymentProvider.query.first()

    if "127.0.0.1" in request.host or "localhost" in request.host:
        # Operate in local mode
        endpoint_secret = current_app.config.get(
            "STRIPE_CLI_WEBHOOK_ENDPOINT_SECRET", None
        )  # noqa
    else:
        if payment_provider.stripe_livemode:
            endpoint_secret = payment_provider.stripe_live_webhook_endpoint_secret
        else:
            endpoint_secret = payment_provider.stripe_test_webhook_endpoint_secret

    if endpoint_secret is None:
        msg = "Could not get endpoint_secret"
        print(msg)
        return jsonify(msg), 500

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", None)
    event = None
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return e, 400
    except stripe.error.SignatureVerificationError as e:
        print(e)
        print("Generating new stripe webhook upon SignatureVerificationError")
        create_stripe_webhook(newWebhookNeeded=True)
        return "Stripe SignatureVerificationError", 400

    print("#" * 20 + "Event" + "#" * 20)
    print(event)
    print("#" * 80)
    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        # Only proces events for this connected account
        if event.account != get_stripe_connect_account().id:
            return "Event account id does not match this shop, ignoring", 200
        session = event["data"]["object"]
        print("#" * 20 + "Session" + "#" * 20)
        print(session)
        print("#" * 100)
        person_uuid = session["metadata"]["person_uuid"]
        person = Person.query.filter_by(uuid=person_uuid).first()
        subscribie_checkout_session_id = session["metadata"][
            "subscribie_checkout_session_id"
        ]

        try:
            chosen_option_ids = session["metadata"]["chosen_option_ids"]
            chosen_option_ids = json.loads(chosen_option_ids)
        except KeyError:
            chosen_option_ids = None
        try:
            package = session["metadata"]["package"]
        except KeyError:
            package = None
        subscription = create_subscription(
            email=session.customer_email,
            package=package,
            chosen_option_ids=chosen_option_ids,
            subscribie_checkout_session_id=subscribie_checkout_session_id,
        )
        print(f"Live mode is: {event['livemode']}, type: {type(event['livemode'])}")

        # Store the transaction
        transaction = Transaction()
        transaction.amount = session["amount_total"]
        transaction.external_id = session.id
        transaction.external_src = "stripe"
        transaction.person = person
        transaction.subscription = subscription
        database.session.add(transaction)
        database.session.commit()

    return "OK", 200


@bp.route("/stripe-create-checkout-session", methods=["POST"])
def stripe_create_checkout_session():
    data = request.json
    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    person = Person.query.get(session["person_id"])
    charge = {}
    charge["sell_price"] = plan.sell_price
    charge["interval_amount"] = plan.interval_amount
    charge["currency"] = "GBP"
    session["subscribie_checkout_session_id"] = str(uuid4())
    stripe.api_key = get_stripe_secret_key()
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": charge["currency"],
                    "product_data": {
                        "name": "(Up-front fee) " + plan.title,
                    },
                    "unit_amount": charge["sell_price"],
                },
                "quantity": 1,
            },
            {
                "price_data": {
                    "recurring": {
                        "interval": format_to_stripe_interval(plan.interval_unit)
                    },
                    "currency": charge["currency"],
                    "product_data": {
                        "name": plan.title,
                    },
                    "unit_amount": charge["interval_amount"],
                },
                "quantity": 1,
            }
        ],
        mode="subscription",
        metadata={
            "person_uuid": person.uuid,
            "plan_uuid": session["plan"],
            "chosen_option_ids": json.dumps(session.get("chosen_option_ids", None)),
            "package": session.get("package", None),
            "subscribie_checkout_session_id": session.get(
                "subscribie_checkout_session_id", None
            ),
        },
        customer_email=person.email,
        success_url=url_for(
            "views.instant_payment_complete", _external=True, plan=plan.uuid
        ),
        # cancel_url is when the customer clicks 'back' in the Stripe checkout ui.
        cancel_url=url_for("views.up_front", _external=True),
        subscription_data={
                "application_fee_percent": 1.25,
                "metadata": {
                    "person_uuid": person.uuid,
                    "plan_uuid": session["plan"],
                    "chosen_option_ids": json.dumps(session.get("chosen_option_ids", None)), # noqa
                    "package": session.get("package", None),
                    "subscribie_checkout_session_id": session.get(
                        "subscribie_checkout_session_id", None
                    ),
                }
        },
        stripe_account=data["account_id"],
    )
    return jsonify(id=stripe_session.id)


@bp.route("/instant_payment_complete", methods=["GET"])
def instant_payment_complete():
    scheme = "https" if request.is_secure else "http"
    return redirect(url_for("views.thankyou", _scheme=scheme, _external=True))


def create_subscription(
    email=None,
    package=None,
    chosen_option_ids=None,
    subscribie_checkout_session_id=None,
) -> Subscription:
    """Create subscription model
    Note: A subscription model is also created if a plan only has
    one up_front payment (no recuring subscription). This allows
    the storing of chosen options againt their plan choice.
    Chosen option ids may be passed via webhook or through session
    """
    print("Creating Subscription model if needed")
    subscription = None  # Initalize subscription model to None

    # Store Subscription against Person locally
    if email is None:
        email = session["email"]

    if package is None:
        package = session["package"]

    person = database.session.query(Person).filter_by(email=email).first()

    # subscribie_checkout_session_id can be passed by stripe metadata (webhook) or
    # via session (e.g. when GoCardless session only with no up-front payment)
    if subscribie_checkout_session_id is None:
        subscribie_checkout_session_id = session.get(
            "subscribie_checkout_session_id", None
        )
    print(f"subscribie_checkout_session_id is: {subscribie_checkout_session_id}")

    # Verify Subscription not already created (e.g. stripe payment webhook)
    # another hook or mandate only payment may have already created the Subscription
    # model, if so, fetch it via its subscribie_checkout_session_id
    if subscribie_checkout_session_id is not None:
        subscription = (
            Subscription.query.filter_by(
                subscribie_checkout_session_id=subscribie_checkout_session_id
            )
            .filter(Subscription.person.has(email=email))
            .first()
        )
        """subscription = (
            database.session.query(Subscription)
            .filter_by(subscribie_checkout_session_id=subscribie_checkout_session_id)
            .has.first()
        )"""

    if subscription is None:
        print("No existing subscription model found, creating Subscription model")
        # Create new subscription model
        subscription = Subscription(
            sku_uuid=package,
            person=person,
            subscribie_checkout_session_id=subscribie_checkout_session_id,
        )
        # Add chosen options (if any)
        if chosen_option_ids is None:
            chosen_option_ids = session.get("chosen_option_ids", None)

        if chosen_option_ids:
            print(f"Applying chosen_option_ids to subscription: {chosen_option_ids}")
            chosen_options = []
            for option_id in chosen_option_ids:
                print(f"Locating option id: {option_id}")
                option = Option.query.get(option_id)
                # Store as ChosenOption because options may change after the order
                # has processed. This preserves integrity of the actual chosen options
                chosen_option = ChosenOption()
                chosen_option.option_title = option.title
                chosen_option.choice_group_title = option.choice_group.title
                chosen_option.choice_group_id = (
                    option.choice_group.id
                )  # Used for grouping latest choice
                chosen_options.append(chosen_option)
            subscription.chosen_options = chosen_options
        else:
            print("No chosen_option_ids were found or applied.")

        database.session.add(subscription)
        database.session.commit()
        session["subscription_uuid"] = subscription.uuid
    return subscription


@bp.route("/thankyou", methods=["GET"])
def thankyou():
    # Remove subscribie_checkout_session_id from session
    session.pop("subscribie_checkout_session_id", None)
    company = Company.query.first()
    plan = Plan.query.filter_by(uuid=session.get("plan", None)).first()
    subscription = (
        database.session.query(Subscription)
        .filter_by(uuid=session.get("subscription_uuid"))
        .first()
    )

    # Store note to seller if in session
    if session.get("note_to_seller", False) is not False and subscription is not None:
        note = SubscriptionNote(
            note=session["note_to_seller"], subscription_id=subscription.id
        )
        database.session.add(note)

    database.session.commit()
    # Send journey_complete signal
    email = session.get("email", current_app.config["MAIL_DEFAULT_SENDER"])
    journey_complete.send(current_app._get_current_object(), email=email)

    # Send welcome email (either default template of custom, if active)
    custom_template = EmailTemplate.query.first()
    if custom_template is not None and custom_template.use_custom_welcome_email is True:
        # Load custom welcome email
        template = custom_template.custom_welcome_email_template
    else:
        # Load default welcome email from template folder
        welcome_template = str(
            Path(current_app.root_path + "/emails/welcome.jinja2.html")
        )
        fp = open(welcome_template)
        template = fp.read()
        fp.close()

    first_charge_date = session.get("first_charge_date", None)
    first_charge_amount = session.get("first_charge_amount", None)
    jinja_template = Template(template)
    scheme = "https://" if request.is_secure else "http://"
    html = jinja_template.render(
        first_name=session.get("given_name", None),
        company_name=company.name,
        subscriber_login_url=scheme + flask.request.host + "/account/login",
        first_charge_date=first_charge_date,
        first_charge_amount=first_charge_amount,
        plan=plan,
    )

    try:
        mail = Mail(current_app)
        msg = Message()
        msg.subject = company.name + " " + "Subscription Confirmation"
        msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
        msg.recipients = [session["email"]]
        setting = Setting.query.first()
        if setting is not None:
            msg.reply_to = setting.reply_to_email_address
        else:
            msg.reply_to = (
                User.query.first().email
            )  # Fallback to first shop admin email
        msg.html = html
        mail.send(msg)
    except Exception as e:
        print(e)
        logging.warning("Failed to send welcome email")

    finally:
        return render_template("thankyou.html")


@bp.route("/page/<path>", methods=["GET"])
def custom_page(path):
    page = Page.query.filter_by(path=path).first()
    # Check if private page & enforce
    blocked, redirect = check_private_page(page.id)
    if blocked:
        return redirect
    try:
        with open(
            Path(str(current_app.config["THEME_PATH"]), page.template_file)
        ) as fh:
            body = fh.read()
    except FileNotFoundError as e:
        print(e)
        return "Template not found for this page.", 404

    page_header = """
        {% extends "layout.html" %}
        {% block title %} {{ title }} {% endblock title %}

        {% block hero %}

            <div class="container">
              <div class="row">
                <div class="col-md-8 pl-0">
                  <h1 class="h1 text-white font-weight-bold">{{ title }}</h1>
                </div>
              </div>
            </div>

        {% endblock %}
        {% block body %}
        <div class="section">
          <div class="container">

    """
    page_footer = """
          </div><!-- end container -->
        </div><!-- end section -->
        {% endblock body %}
    """
    try:
        rtemplate = Environment(
            loader=FileSystemLoader(str(current_app.config["THEME_PATH"]))
        ).from_string(page_header + body + page_footer)
    except jinja2.exceptions.TemplateAssertionError as e:
        return f"Page needs updating: {e}"

    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    template = rtemplate.render(
        company=company,
        integration=integration,
        plans=plans,
        pages=pages,
        session=session,
        g=g,
        url_for=url_for,
        title=page.page_name,
    )

    return template
