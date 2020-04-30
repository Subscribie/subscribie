from . import logger
import os
import yaml
import datetime
from datetime import date
import sqlite3
from .signals import journey_complete
from subscribie import Jamla, session, CustomerForm, gocardless_pro, current_app
from subscribie.db import get_jamla, get_db
import stripe
from dingdb import dingdb
from uuid import uuid4
from pathlib import Path

from flask import Blueprint, redirect, render_template, request, session, url_for, flash

from .models import database, User, Person, Subscription

from flask_mail import Mail, Message

bp = Blueprint("views", __name__, url_prefix=None)


def redirect_url(default='index'):
    return request.args.get('next') or \
        request.referrer or \
        url_for('index')

def index():
    jamla = get_jamla()
    return render_template("index.html", jamla=jamla)

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
    jamla = get_jamla()
    # Filter archived items
    jamlaApp = Jamla()
    jamla = jamlaApp.filter_archived_items(jamla)

    return render_template("choose.html", jamla=jamla, pages=jamla['pages'])


@bp.route("/new_customer", methods=["GET"])
def new_customer():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    jamla = jamlaApp.filter_archived_items(jamla)
    package = request.args.get("plan", "not set")
    session["package"] = package
    session["item"] = jamlaApp.sku_get_by_uuid(package)
    form = CustomerForm()
    return render_template("new_customer.html", jamla=jamla, form=form, package=package,
                         item=session["item"],
                         pages=jamla['pages'])


@bp.route("/new_customer", methods=["POST"])
def store_customer():
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

        # Store plan in session
        jamlaApp = Jamla()
        jamla = get_jamla()
        jamlaApp.load(jamla=jamla)
        if jamlaApp.sku_uuid_exists(request.args.get("plan")):
            wants = request.args.get("plan")
            session["plan"] = wants
        person = Person(sid=sid, given_name=given_name, family_name=family_name,
                        address_line1=address_line_one, city=city,
                        postal_code=postcode, email=email, mobile=mobile)
        database.session.add(person)
        database.session.commit()
        # Store note to seller in session if there is one
        note_to_seller = form.data["note_to_seller"]
        session["note_to_seller"] = note_to_seller
        if jamlaApp.requires_instantpayment(session["package"]):
            return redirect(
                url_for(
                    "views.up_front",
                    _scheme="https",
                    _external=True,
                    sid=sid,
                    package=wants,
                    fname=given_name,
                )
            )
        if jamlaApp.requires_subscription(session["package"]):
            # Check if in iframe
            if form.data["is_iframe"] == "True":
                insideIframe = True
            else:
                insideIframe = False
            return redirect(url_for("views.establish_mandate", inside_iframe=insideIframe))
        return redirect(url_for("views.thankyou", _scheme="https", _external=True))
    else:
        return "Oops, there was an error processing that form, please go back and try again."


@bp.route("/up_front/<sid>/<package>/<fname>", methods=["GET"])
def up_front(sid, package, fname):
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    selling_points = jamlaApp.get_selling_points(package)
    upfront_cost = jamlaApp.sku_get_upfront_cost(package)
    monthly_cost = jamlaApp.sku_get_monthly_price(package)
    stripe_pub_key = jamla["payment_providers"]["stripe"]["publishable_key"]
    session["upfront_cost"] = upfront_cost
    session["monthly_cost"] = monthly_cost

    return render_template(
        "up_front_payment.html",
        jamla=jamla,
        item=session['item'],
        fname=fname,
        selling_points=selling_points,
        upfront_cost=upfront_cost,
        monthly_cost=monthly_cost,
        sid=sid,
        stripe_pub_key=stripe_pub_key,
        pages=jamla['pages']
    )


@bp.route("/up_front", methods=["POST"])
def charge_up_front():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    charge = {}
    charge["amount"] = session["upfront_cost"]
    charge["currency"] = "GBP"

    sid = session["sid"]

    db = get_db()
    res = db.execute("SELECT * FROM person p WHERE p.sid = ?", (sid,)).fetchone()
    try:
        stripe.api_key = jamla["payment_providers"]["stripe"]["secret_key"]
        customer = stripe.Customer.create(
            email=res["email"], source=request.form["stripeToken"]
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=charge["amount"],
            currency=charge["currency"],
            description="Subscribie",
        )
    except stripe.error.AuthenticationError as e:
        return str(e)
    if jamlaApp.requires_subscription(session["package"]):
        return redirect(url_for("views.establish_mandate"))
    else:
        return redirect(url_for("views.thankyou", _scheme="https", _external=True))


@bp.route("/establish_mandate", methods=["GET"])
def establish_mandate():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)

    if jamlaApp.has_connected("gocardless") is False:
        dashboard_url = url_for("admin.dashboard")
        return """<h1>Shop not set-up yet</h1>
            The shop owner first needs to login to their
            <a href="{}">dahboard</a>, and connect GoCardless to their shop.
            Once this has been completed, you will be able to order.
        """.format(
            dashboard_url
        )

    # lookup the customer with sid and get their relevant details
    sid = session["sid"]
    db = get_db()
    res = db.execute("SELECT * FROM person p WHERE p.sid = ?", (sid,)).fetchone()

    logger.info("Person lookup: %s", res)
    # validate that hasInstantPaid is true for the customer
    gocclient = gocardless_pro.Client(
        access_token=jamlaApp.get_secret("gocardless", "access_token"),
        environment=jamla["payment_providers"]["gocardless"]["environment"],
    )

    description = " ".join([jamla["company"]["name"], session["package"]])[0:100]
    redirect_flow = gocclient.redirect_flows.create(
        params={
            "description": description,
            "session_token": sid,
            "success_redirect_url": current_app.config["SUCCESS_REDIRECT_URL"],
            "prefilled_customer": {
                "given_name": res["given_name"],
                "family_name": res["family_name"],
                "address_line1": res["address_line1"],
                "city": res["city"],
                "postal_code": res["postal_code"],
                "email": res["email"],
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
                                redirect_url=redirect_flow.redirect_url,
                                jamla=jamla)
        return '<a href="{}" target="_blank">Continue</a>'.format(redirect_flow.redirect_url)
    else:
        return redirect(redirect_flow.redirect_url)


@bp.route("/complete_mandate", methods=["GET"])
def on_complete_mandate():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    redirect_flow_id = request.args.get("redirect_flow_id")
    logger.info("Recieved flow ID: %s ", redirect_flow_id)

    logger.info(
        "Setting up client environment as: %s",
        jamla["payment_providers"]["gocardless"]["environment"],
    )
    gocclient = gocardless_pro.Client(
        access_token=jamlaApp.get_secret("gocardless", "access_token"),
        environment=jamla["payment_providers"]["gocardless"]["environment"],
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
            str(jamlaApp.sku_get_monthly_price(session["plan"])),
        )
        logger.info(
            "Creating subscription with name: %s",
            jamlaApp.sku_get_title(session["plan"]),
        )
        logger.info("Plan session is set to: %s", str(session["plan"]))
        logger.info("Mandate id is set to: %s", session["gocardless_mandate_id"])

        # If days_before_first_charge is set, apply start_date adjustment
        itemIndex = jamlaApp.sku_get_index(session['plan'])
        try:
            days_before_first_charge = jamla['items'][itemIndex]['days_before_first_charge']
            if days_before_first_charge == 0 or days_before_first_charge == '':
                start_date = None
            else:
                today = date.today()
                enddate = today + datetime.timedelta(days=int(days_before_first_charge))
                start_date = enddate.strftime('%Y-%m-%d')
        except KeyError:
            start_date = None

        # Create subscription
        print("Creating subscription")
        # Store Subscription against Person locally
        person = database.session.query(Person).filter_by(email=session['email']).first()
        subscription = Subscription(sku_uuid=session['package'], person=person)
        database.session.add(subscription)
        database.session.commit()

        # Submit to GoCardless as subscription
        gc_subscription = gocclient.subscriptions.create(
            params={
                "amount": int(jamlaApp.sku_get_monthly_price(session["plan"])),
                "currency": "GBP",
                "name": jamlaApp.sku_get_title(session["plan"]),
                "interval_unit": "monthly",
                "metadata": {"subscribie_subscription_uuid": subscription.uuid},
                "links": {"mandate": session["gocardless_mandate_id"]},
                "start_date" : start_date
            }
        )
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


@bp.route("/thankyou", methods=["GET"])
def thankyou():
    jamla = get_jamla()

    # Store note to seller if in session
    if session.get('note_to_seller', False) is not False:
      tdb = dingdb(database=current_app.config["DB_FULL_PATH"])
      tdb.putDing(str(uuid4()), 'orderNote', 'orderNote', data=[{'key':'email', 'value': session["email"]}, {'key':'note', 'value':session["note_to_seller"]}])
    # Send journey_complete signal
    journey_complete.send(current_app._get_current_object(), email=session["email"])
    # Send welcome email
    html = """
    <html>
        <head></head>
        <body>
        <h1>Subscription Confirmation</h1>
        <p>This email confirms that your subscription with {company}
           is now setup.</p>
        <p>If you have any questions, please respond to this email.</p>
    """.format(company=jamla["company"]["name"])

    try:
        mail = Mail(current_app)
        msg = Message()
        msg.subject = jamla["company"]["name"] + " " + "Subscription Confirmation"
        msg.sender = current_app.config["EMAIL_LOGIN_FROM"]
        msg.recipients = [session["email"]]
        msg.reply_to = User.query.first().email
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
        logger.warning("Maybe OK as not all items require a direct debit mandate")
    finally:
        return render_template("thankyou.html", jamla=jamla, pages=jamla['pages'])
