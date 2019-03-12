import os
import yaml
import datetime
import sqlite3
from signals import journey_complete
from subscribie import Jamla, session, \
     CustomerForm, gocardless_pro, \
     current_app 
from subscribie.db import get_jamla, get_db
import stripe

from flask import (                                                              
    Blueprint, redirect, render_template, request, session, url_for       
)                                                                                

bp = Blueprint('views', __name__, url_prefix=None)

def index():
    jamla = get_jamla()
    return render_template('index.html', jamla=jamla)

@bp.route('/choose')
def choose():
    jamla = get_jamla()
    return render_template('choose.html', jamla=jamla)

@bp.route('/new_customer', methods=['GET'])
def new_customer():
    jamla = get_jamla()
    package = request.args.get('plan','not set')
    session['package'] = package
    form = CustomerForm()
    return render_template('new_customer.html', jamla=jamla, form=form, package=package)

@bp.route('/new_customer', methods=['POST'])
def store_customer():
    form = CustomerForm()
    if form.validate():
        given_name = form.data['given_name']
        family_name = form.data['family_name']
        address_line_one = form.data['address_line_one']
        city = form.data['city']
        postcode = form.data['postcode']
        email = form.data['email']
        mobile = form.data['mobile']
        now = datetime.datetime.now()
        # Store customer in session
        sid = session['sid']
        # Store email in session
        session['email'] = email

        # Store plan in session
	jamlaApp = Jamla()
        jamla = get_jamla()
        jamlaApp.load(jamla=jamla)
        if jamlaApp.sku_exists(request.args.get('plan')):
            wants = request.args.get('plan')
            session['plan'] = wants
        db = get_db()
        db.execute("INSERT INTO person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (sid, now, given_name, family_name,
                    address_line_one, city, postcode, email, mobile,
                    wants, 'null', 'null', False))
        db.commit()

        if jamlaApp.requires_instantpayment(session['package']):
            return redirect(url_for('views.up_front', _scheme='https', _external=True, sid=sid, package=wants, fname=given_name))
        if jamlaApp.requires_subscription(session['package']):
            return redirect(url_for('views.establish_mandate'))
        return redirect(url_for('views.thankyou', _scheme='https', _external=True))
    else:
        return "Oops, there was an error processing that form, please go back and try again."


@bp.route('/up_front/<sid>/<package>/<fname>', methods=['GET'])
def up_front(sid, package, fname):
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    selling_points = jamlaApp.get_selling_points(package)
    upfront_cost = jamlaApp.sku_get_upfront_cost(package)
    monthly_cost = jamlaApp.sku_get_monthly_price(package)
    stripe_pub_key = jamla['payment_providers']['stripe']['publishable_key']
    session['upfront_cost'] = upfront_cost
    session['monthly_cost'] = monthly_cost

    return render_template('up_front_payment.html', jamla=jamla,package=package,
                           fname=fname, selling_points=selling_points,
                           upfront_cost=upfront_cost, monthly_cost=monthly_cost,
                           sid=sid, stripe_pub_key=stripe_pub_key)

@bp.route('/up_front', methods=['POST'])
def charge_up_front():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    charge = {}
    charge['amount'] = session['upfront_cost']
    charge['currency'] = "GBP"

    sid = session['sid']

    db = get_db()                                                                
    res = db.execute("SELECT * FROM person p WHERE p.sid = ?", (sid,)
    ).fetchone()                                                             
    try:
        stripe.api_key = jamla['payment_providers']['stripe']['secret_key']
        customer = stripe.Customer.create(
            email=res['email'],
            source=request.form['stripeToken']
        )

        charge = stripe.Charge.create(
            customer=customer.id,
            amount=charge['amount'],
            currency=charge['currency'],
            description='Subscribie'
        )
    except stripe.error.AuthenticationError as e:
        return str(e)
    if jamlaApp.requires_subscription(session['package']):
        return redirect(url_for('views.establish_mandate'))
    else:
        return redirect(url_for('views.thankyou', _scheme='https', _external=True))

@bp.route('/establish_mandate', methods=['GET'])
def establish_mandate():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)

    if jamlaApp.has_connected('gocardless') is False:
        dashboard_url = url_for('admin.dashboard')
        return '''<h1>Shop not set-up yet</h1>
            The shop owner first needs to login to their
            <a href="{}">dahboard</a>, and connect GoCardless to their shop.
            Once this has been completed, you will be able to order.
        '''.format(dashboard_url)

    #lookup the customer with sid and get their relevant details
    sid = session['sid']
    db = get_db()                                                                
    res = db.execute("SELECT * FROM person p WHERE p.sid = ?", (sid,)
                     ).fetchone()

    print res
    # validate that hasInstantPaid is true for the customer
    gocclient = gocardless_pro.Client(
        access_token = jamlaApp.get_secret('gocardless', 'access_token'),
        environment= jamla['payment_providers']['gocardless']['environment']
    )

    description = ' '.join([jamla['company']['name'],session['package']])[0:100]
    redirect_flow = gocclient.redirect_flows.create(
        params = {
            "description" : description,
            "session_token" : sid,
            "success_redirect_url" : current_app.config['SUCCESS_REDIRECT_URL'],
            "prefilled_customer" : {
                "given_name" : res['given_name'],
                "family_name": res['family_name'],
                "address_line1": res['address_line1'],
                "city" : res['city'],
                "postal_code": res['postal_code'],
                "email": res['email']
            }
        }
    )
    # Hold on to this ID - we'll need it when we
    # "confirm" the dedirect flow later
    print("ID: {} ".format(redirect_flow.id))
    print("URL: {} ".format(redirect_flow.redirect_url))
    return redirect(redirect_flow.redirect_url)

@bp.route('/complete_mandate', methods=['GET'])
def on_complete_mandate():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    redirect_flow_id = request.args.get('redirect_flow_id')
    print("Recieved flow ID: {} ".format(redirect_flow_id))

    print "Setting up client environment as: " + jamla['payment_providers']['gocardless']['environment']
    gocclient = gocardless_pro.Client(
        access_token = jamlaApp.get_secret('gocardless', 'access_token'),
        environment = jamla['payment_providers']['gocardless']['environment']
    )
    try:
        redirect_flow = gocclient.redirect_flows.complete(
            redirect_flow_id,
            params = {
                "session_token": session['sid']
        })
        print("Confirmation URL: {}".format(redirect_flow.confirmation_url))
        # Save this mandate & customer ID for the next section.
        print ("Mandate: {}".format(redirect_flow.links.mandate))
        print ("Customer: {}".format(redirect_flow.links.customer))
        session['gocardless_mandate_id'] = redirect_flow.links.mandate
        session['gocardless_customer_id'] = redirect_flow.links.customer
        # Store customer
        sid = session['sid']
        now = datetime.datetime.now()
        mandate = redirect_flow.links.mandate
        customer = redirect_flow.links.customer
        flow = redirect_flow_id

        con = sqlite3.connect(current_app.config['DB_FULL_PATH'])
        cur = con.cursor()
        cur.execute("SELECT * FROM person WHERE sid = ?", (sid,))
        row = cur.fetchone()
        customerName = row[2] + " " + row[3]
        customerAddress = row[4] + ", " + row[5] + ", " + row[6]
        customerEmail = row[7]
        customerPhone = row[8]
        chosenPackage = row[9]
        customerExistingLine = row[10]
        customerExistingNumber = row[11]

        print "Creating subscription with amount: " + str(jamlaApp.sku_get_monthly_price(session['plan']))
        print "Creating subscription with name: " + jamlaApp.sku_get_title(session['plan'])
        print "Plan session is set to: " + str(session['plan'])
        print "Mandate id is set to: " + session['gocardless_mandate_id']

        # Create subscription
        gocclient.subscriptions.create(params={
            "amount":jamlaApp.sku_get_monthly_price(session['plan']),
            "currency":"GBP",
            "name": jamlaApp.sku_get_title(session['plan']),
            "interval_unit": "monthly",
            "metadata": {
                "sku":session['plan']
            },
            "links": {
                "mandate":session['gocardless_mandate_id']
            }
        })
    except Exception as e:
        print e
        if isinstance(e, gocardless_pro.errors.InvalidStateError):
            if e.error['type'] == 'invalid_state':
                # Allow pass through if redirect flow already completed
                if e.errors[0]['reason'] == "redirect_flow_already_completed":
                    pass
    # Display a confirmation page to the customer, telling them
    # their Direct Debit has been set up.
    return redirect(current_app.config['THANKYOU_URL'])

@bp.route('/thankyou', methods=['GET'])
def thankyou():
    jamla = get_jamla()
    # Send journey_complete signal
    journey_complete.send(current_app._get_current_object(), email=session['email'])
    try:
        print "##### The Mandate id is:" + str(session['gocardless_mandate_id'])
        print "##### The GC Customer id is: " + str(session['gocardless_customer_id'])
    except KeyError:
        print
        print "##### No mandate for this transaction"
        print " (OK as not all items require a direct debit mandate)"
        print "#####"
    finally:
        return render_template('thankyou.html', jamla=jamla)
