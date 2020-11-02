from . import logger
import os
import yaml
import datetime
from datetime import date
import sqlite3
from .signals import journey_complete
from subscribie import session, CustomerForm, gocardless_pro, current_app
import stripe
from uuid import uuid4
from pathlib import Path
from jinja2 import Template

from flask import Blueprint, redirect, render_template, request, session, url_for, flash, jsonify, g
import flask

from .models import ( database, User, Person, Subscription, SubscriptionNote,
                    Company, Plan, Integration, PaymentProvider, Transaction,
                    Page, Option, ChosenOption, EmailTemplate, Setting)

from flask_mail import Mail, Message
from sqlalchemy.sql.expression import func
from typing import Optional
import json

bp = Blueprint("views", __name__, url_prefix=None)

@bp.before_app_request
def check_if_inside_iframe():
    """Set iframe_embeded in session object if app is loaded from inside an iframe
    If visited directly, (e.g. as a shop admin),
    then referer header is emtpy, and therefore the header/footer is 
    displayed as normal.
    """
    if request.args.get('iframe_embeded', False) or session.get('iframe_embeded') is True and request.headers.get('referer') is not None:
        print("Loading from within iframe")
        session['iframe_embeded'] = True
    else:
        session['iframe_embeded'] = False

@bp.app_context_processor
def inject_template_globals():
    company = Company.query.first()
    integration = Integration.query.first()
    plans = Plan.query.filter_by(archived=0)
    pages = Page.query.all()
    return dict(company=company, integration=integration, plans=plans,
                pages=pages)

def redirect_url(default='index'):
    return request.args.get('next') or \
        request.referrer or \
        url_for('index')

def index():
    return render_template("index.html")


@bp.route("/reload")
def reload_app():
    """Reload app
    when running as a uwsgi vassal, a touch is performed
    on the app's .ini file to trigger a graceful reload of 
    the app"""
    path = os.path.abspath(__file__ + "../../../../")
    # .ini file is named <hostname>.ini
    vassalFilePath = Path(path , request.host + '.ini')
    # Perform reload by touching file
    print("Reloading by touching ini file at {}".format(vassalFilePath))
    vassalFilePath.touch(exist_ok=True)
    flash("Reload triggered")
    return redirect(redirect_url())
    

@bp.route("/choose")
def choose():
    plans = Plan.query.filter_by(archived=0).order_by(Plan.position).all()
    return render_template("choose.html",
                            plans=plans)

def redirect_to_payment_step(plan, inside_iframe=False):
    """Depending on plans payment requirement, redirect to collection page
     accordingly"""

    scheme = 'https' if request.is_secure else 'http'

    if plan.requirements.instant_payment:
        return redirect(
            url_for(
                "views.up_front",
                _scheme=scheme,
                _external=True
            )
        )
    if plan.requirements.subscription:
        return redirect(url_for("views.establish_mandate", inside_iframe=inside_iframe))
    return redirect(url_for("views.thankyou", _scheme=scheme, _external=True))

@bp.route("/new_customer", methods=["GET"])
def new_customer():
    plan = Plan.query.filter_by(uuid=request.args['plan']).first()
    session["plan"] = plan.uuid

    # Fetch selected options, if present
    chosen_options = []
    if session.get('chosen_option_ids', None):
        for option_id in session['chosen_option_ids']:
            option = Option.query.get(option_id)
            # We will store as ChosenOption because option may change after the order has processed
            # This preserves integrity of the actual chosen options
            chosen_option = ChosenOption()
            chosen_option.option_title = option.title
            chosen_option.choice_group_title = option.choice_group.title
            chosen_options.append(chosen_option)
    
    # If already entered sign-up information, take to payment step
    if session.get("person_id", None):
        return redirect_to_payment_step(plan)


    package = request.args.get("plan", "not set")
    session["package"] = package
    plan = Plan.query.filter_by(uuid=request.args.get('plan')).first()
    form = CustomerForm()
    return render_template("new_customer.html", form=form, package=package,
                         plan=plan,
                         chosen_options=chosen_options)


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
        session['given_name'] = given_name
        session['family_name'] = family_name
        session['address_line_one'] = address_line_one
        session['city'] = city
        session['postcode'] = postcode
        session['email'] = email
        session['mobile'] = mobile

        # Don't store person if already exists
        person = Person.query.filter_by(email=email).first()
        if person is None:
            # Store person, with randomly generated password
            person = Person(sid=sid, given_name=given_name, family_name=family_name,
                            address_line1=address_line_one, city=city,
                            postal_code=postcode, email=email, mobile=mobile,
                            password=str(os.urandom(16)))
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
        return "Oops, there was an error processing that form, please go back and try again."

@bp.route("/set_options/<plan_uuid>", methods=["GET", "POST"])
def set_options(plan_uuid):
    plan = Plan.query.filter_by(uuid=plan_uuid).first()

    if request.method == "POST":
        # Store chosen options in session
        session['chosen_option_ids'] = []
        for choice_group_id in request.form.keys():
            for option_id in request.form.getlist(choice_group_id):
                session['chosen_option_ids'].append(option_id)


        return redirect(url_for('views.new_customer', plan=plan_uuid))

    return render_template("set_options.html", plan=plan)


@bp.route("/up_front", methods=["GET"])
def up_front():
    payment_provider = PaymentProvider.query.first()
    if payment_provider.stripe_connect_account_id is None:
        return """Shop owner has not connected Stripe payments yet.
                This can be done by the shop owner via the admin dashboard."""

    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    stripe_pub_key = current_app.config.get('STRIPE_PUBLISHABLE_KEY')
    company = Company.query.first()
    stripe_create_checkout_session_url = url_for('views.stripe_create_checkout_session')

    stripe_connected_account_id = payment_provider.stripe_connect_account_id

    return render_template(
        "up_front_payment.html",
        company=company,
        plan=plan,
        fname=session["given_name"],
        stripe_pub_key=stripe_pub_key,
        stripe_create_checkout_session_url=stripe_create_checkout_session_url,
        stripe_connected_account_id=stripe_connected_account_id
    )


@bp.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    payment_provider = PaymentProvider.query.first()
    stripe_account_id = payment_provider.stripe_connect_account_id

    if current_app.config.get("STRIPE_WEBHOOK_ENDPOINT_SECRET", None):
        endpoint_secret  = current_app.config.get("STRIPE_WEBHOOK_ENDPOINT_SECRET", None)
    else:
        endpoint_secret = payment_provider.stripe_webhook_endpoint_secret
        if endpoint_secret is None:
            msg = "Could not fetch stripe_webhook_endpoint_secret from db"
            print(msg)
            return jsonify(msg), 500

    payload = request.data
    sig_header = request.headers.get("Stripe-Signature", None)
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        return e, 400
    except stripe.error.SignatureVerificationError as e:
        return "Stripe ignatureVerificationError", 400

    print("#"*20 + "Event" + "#"*20)
    print(event)
    print("#"*80)
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Only proces events for this connected account
        if event.account != payment_provider.stripe_connect_account_id:
            return "Event account id does not match this shop, ignoring", 200
        session = event['data']['object']
        print("#"*20 + "Session" + "#"*20)
        print(session)
        print("#"*100)
        plan_uuid = session['metadata']['plan_uuid']
        person_uuid = session['metadata']['person_uuid']
        plan = Plan.query.filter_by(uuid=plan_uuid).first()
        person = Person.query.filter_by(uuid=person_uuid).first()

        try:
            chosen_option_ids = session['metadata']['chosen_option_ids']
            chosen_option_ids = json.loads(chosen_option_ids)
        except KeyError:
            chosen_option_ids = None
        try:
            package = session['metadata']['package']
        except KeyError:
            package = None
        subscription = create_subscription(email=session.customer_email,
                                           package=package,
                                           chosen_option_ids=chosen_option_ids)

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
    payment_provider = PaymentProvider.query.first()
    data = request.json
    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    person = Person.query.get(session["person_id"])
    charge = {}
    charge["amount"] = plan.sell_price
    charge["currency"] = "GBP"
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')
    stripe_session = stripe.checkout.Session.create(
        payment_method_types = ["card"],
        line_items=[{
            'price_data': {
                'currency': charge['currency'],
                'product_data': {
                    'name': plan.title,
                },
                'unit_amount': charge['amount']
            },
            'quantity': 1,
        }],
        mode='payment',
        metadata={"person_uuid": person.uuid,
                  "plan_uuid": session["plan"],
                  "chosen_option_ids": json.dumps(session.get('chosen_option_ids', None)),
                  "package": session.get('package', None)
                 },
        customer_email = person.email,
        success_url = url_for('views.instant_payment_complete', _external=True, plan=plan.uuid),
        # cancel_url is when the customer clicks 'back' in the Stripe checkout ui.
        cancel_url = url_for('views.up_front', _external=True),
        payment_intent_data = {
            'application_fee_amount': 20
        },
        stripe_account=data['account_id']
    )
    return jsonify(id=stripe_session.id)


@bp.route("/instant_payment_complete", methods=["GET"])
def instant_payment_complete():

    plan_uuid = request.args.get('plan')
    plan = Plan.query.filter_by(uuid=plan_uuid).first()
    if plan.requirements.subscription:
        return redirect(url_for("views.establish_mandate"))
    else:
        scheme = 'https' if request.is_secure else 'http'
        return redirect(url_for("views.thankyou", _scheme=scheme, _external=True))


@bp.route("/establish_mandate", methods=["GET"])
def establish_mandate():
    company = Company.query.first()
    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    payment_provider = PaymentProvider.query.first()

    if payment_provider.gocardless_active is False:
        dashboard_url = url_for("admin.dashboard")
        return """<h1>Shop not set-up yet</h1>
            The shop owner first needs to login to their
            <a href="{}">dahboard</a>, and connect GoCardless to their shop.
            Once this has been completed, you will be able to order.
        """.format(
            dashboard_url
        )

    # Get person from session
    person = Person.query.get(session["person_id"])

    # validate that hasInstantPaid is true for the customer
    gocclient = gocardless_pro.Client(
        access_token=payment_provider.gocardless_access_token,
        environment=payment_provider.gocardless_environment,
    )

    description = " ".join([company.name, plan.title])[0:100]
    redirect_flow = gocclient.redirect_flows.create(
        params={
            "description": description,
            "session_token": session["sid"],
            "success_redirect_url": current_app.config["SUCCESS_REDIRECT_URL"],
            "prefilled_customer": {
                "given_name": person.given_name,
                "family_name": person.family_name,
                "address_line1": person.address_line1,
                "city": person.city,
                "postal_code": person.postal_code,
                "email": person.email,
            },
        }
    )
    # Hold on to this ID - we'll need it when we
    # "confirm" the dedirect flow later
    print("ID: {} ".format(redirect_flow.id))
    print("URL: {} ".format(redirect_flow.redirect_url))

    # Check if we're inside an iframe, if yes redirect to pop-up
    # Issue https://github.com/Subscribie/subscribie/issues/128
    if request.args.get('inside_iframe', 'False') == "True":
        inside_iframe = True
        return render_template("iframe_new_window_redirect.html", 
                                redirect_url=redirect_flow.redirect_url)
        return '<a href="{}" target="_blank">Continue</a>'.format(redirect_flow.redirect_url)
    else:
        return redirect(redirect_flow.redirect_url)


@bp.route("/complete_mandate", methods=["GET"])
def on_complete_mandate():
    plan = Plan.query.filter_by(uuid=session["plan"]).first()
    payment_provider = PaymentProvider.query.first()
    redirect_flow_id = request.args.get("redirect_flow_id")
    logger.info("Recieved flow ID: %s ", redirect_flow_id)

    logger.info(
        "Setting up client environment as: %s",
        payment_provider.gocardless_environment,
    )
    gocclient = gocardless_pro.Client(
        access_token=payment_provider.gocardless_access_token,
        environment=payment_provider.gocardless_environment,
    )
    try:
        redirect_flow = gocclient.redirect_flows.complete(
            redirect_flow_id, params={"session_token": session["sid"]}
        )
        logger.info("Confirmation URL: %s", redirect_flow.confirmation_url)
        # Save this mandate & customer ID for the next section.
        logger.info("Mandate: %s", redirect_flow.links.mandate)
        logger.info("Customer: %s", redirect_flow.links.customer)
        session["gocardless_mandate_id"] = redirect_flow.links.mandate
        session["gocardless_customer_id"] = redirect_flow.links.customer
        # Store customer
        sid = session["sid"]
        now = datetime.datetime.now()
        mandate = redirect_flow.links.mandate
        customer = redirect_flow.links.customer
        flow = redirect_flow_id

        logger.info(
            "Creating subscription with amount: %s",
            str(plan.interval_amount),
        )
        logger.info(
            "Creating subscription with name: %s",
            plan.title,
        )
        logger.info("Plan session is set to: %s", str(session["plan"]))
        logger.info("Mandate id is set to: %s", session["gocardless_mandate_id"])

        # If days_before_first_charge is set, apply start_date adjustment
        try:
            days_before_first_charge = plan.days_before_first_charge
            if days_before_first_charge == 0 or days_before_first_charge == '' or days_before_first_charge == None:
                start_date = None
            else:
                today = date.today()
                enddate = today + datetime.timedelta(days=int(days_before_first_charge))
                start_date = enddate.strftime('%Y-%m-%d')
        except KeyError:
            start_date = None

        subscription = create_subscription()

        # Get interval_unit
        if plan.interval_unit is None:
            # Default to monthly interval if interval_unit not set
            interval_unit = "monthly"
        else:
            interval_unit = plan.interval_unit

        # Get interval_amount
        if plan.interval_amount is None:
            # Default to monthly amount if interval_amount is not set
            interval_amount = plan.monthly_price
        else:
            interval_amount = plan.interval_amount

        # Submit to GoCardless as subscription
        gc_subscription = gocclient.subscriptions.create(
            params={
                "amount": interval_amount,
                "currency": "GBP",
                "name": plan.title,
                "interval_unit": interval_unit,
                "metadata": {"subscribie_subscription_uuid": subscription.uuid},
                "links": {"mandate": session["gocardless_mandate_id"]},
                "start_date" : start_date
            }
        )
        # Get first charge date & store in session
        first_charge_date = gc_subscription.upcoming_payments[0]['charge_date']
        first_charge_amount = gc_subscription.upcoming_payments[0]['amount']
        session['first_charge_date'] = str(datetime.datetime.strptime(first_charge_date, '%Y-%m-%d').strftime('%d/%m/%Y'))
        session['first_charge_amount'] = first_charge_amount
        # Store GoCardless subscription id
        subscription.gocardless_subscription_id = gc_subscription.id
        database.session.add(subscription)
        database.session.commit()


    except Exception as e:
        logger.error(e)
        if isinstance(e, gocardless_pro.errors.InvalidStateError):
            if e.error["type"] == "invalid_state":
                # Allow pass through if redirect flow already completed
                if e.errors[0]["reason"] == "redirect_flow_already_completed":
                    pass
    # Display a confirmation page to the customer, telling them
    # their Direct Debit has been set up.
    return redirect(current_app.config["THANKYOU_URL"])

def create_subscription(email=None, package=None, chosen_option_ids=None) -> Subscription:
    '''Create subscription model
    Note: A subscription model is also created if a plan only has
    one up_front payment (no recuring subscription). This allows
    the storing of chosen options againt their plan choice.'''
    print("Creating subscription")
    # Store Subscription against Person locally
    if email is None:
        email = session['email']

    if package is None:
        package = session['package']

    person = database.session.query(Person).filter_by(email=email).first()
    subscription = Subscription(sku_uuid=package, person=person)

    # Add chosen options (if any)
    chosen_options = []
    if session.get('chosen_option_ids', None) or chosen_option_ids: # May be passed via webhook
        for option_id in chosen_option_ids:
            print(f"Locating option id: {option_id}")
            option = Option.query.get(option_id)
            # We will store as ChosenOption because option may change after the order has processed
            # This preserves integrity of the actual chosen options
            chosen_option = ChosenOption()
            chosen_option.option_title = option.title
            chosen_option.choice_group_title = option.choice_group.title
            chosen_option.choice_group_id = option.choice_group.id # Used for grouping latest choice
            chosen_options.append(chosen_option)    
    subscription.chosen_options = chosen_options

    database.session.add(subscription)
    database.session.commit()
    session['subscription_uuid'] = subscription.uuid
    return subscription

@bp.route("/thankyou", methods=["GET"])
def thankyou():
    company = Company.query.first()
    plan = Plan.query.filter_by(uuid=session.get('plan', None)).first()
    subscription = database.session.query(Subscription).filter_by(uuid=session.get('subscription_uuid')).first()

    # Store note to seller if in session
    if session.get('note_to_seller', False) is not False and \
      subscription is not None:
      note = SubscriptionNote(note=session["note_to_seller"],
                             subscription_id=subscription.id)
      database.session.add(note)

    database.session.commit()
    # Send journey_complete signal
    email = session.get("email", current_app.config["MAIL_DEFAULT_SENDER"])
    journey_complete.send(current_app._get_current_object(), email=email)

    #Send welcome email (either default template of custom, if active)
    custom_template = EmailTemplate.query.first()
    if custom_template is not None and custom_template.use_custom_welcome_email is True:
        # Load custom welcome email
        template = custom_template.custom_welcome_email_template
    else:
        # Load default welcome email from template folder 
        welcome_template = str(Path(current_app.root_path + '/emails/welcome.jinja2.html'))
        fp = open(welcome_template)
        template = fp.read()
        fp.close()

    first_charge_date = session.get('first_charge_date', None)
    first_charge_amount = session.get('first_charge_amount', None)
    jinja_template = Template(template)
    scheme = 'https://' if request.is_secure else 'http://'
    html = jinja_template.render(first_name=session.get('given_name', None), 
                company_name=company.name,
                subscriber_login_url=scheme + flask.request.host + '/account/login',
                first_charge_date=first_charge_date,
                first_charge_amount=first_charge_amount,
                plan=plan)

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
            msg.reply_to = User.query.first().email # Fallback to first shop admin email
        msg.html = html
        mail.send(msg)
    except Exception as e:
        print(e)
        logger.warning("Failed to send welcome email")

    try:
        logger.info("The Mandate id is: %s", str(session["gocardless_mandate_id"]))
        logger.info("The GC Customer id is: %s", str(session["gocardless_customer_id"]))
    except KeyError:
        logger.warning("No mandate for this transaction")
        logger.warning("Maybe OK as not all plans require a direct debit mandate")
    finally:
        return render_template("thankyou.html")
