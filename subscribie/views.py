import functools
import os
import yaml
import datetime
import random
import sqlite3
import smtplib
from signals import journey_complete
from subscribie import Jamla, session, render_template, \
     request, redirect, CustomerForm, LoginForm, gocardless_pro, \
     GocardlessConnectForm, StripeConnectForm, current_app, \
     redirect, url_for, StripeConnectForm, ItemsForm, send_from_directory, \
     jsonify
from subscribie.db import get_jamla, get_db
from base64 import b64encode, urlsafe_b64encode
from flask_uploads import configure_uploads, UploadSet, IMAGES
import stripe
from auth import login_required

from flask import (                                                              
    Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for       
)                                                                                
from werkzeug.security import check_password_hash, generate_password_hash        
                                                                                 
bp = Blueprint('views', __name__, url_prefix=None)

@bp.route('/')
def choose():
    jamla = get_jamla()
    session['sid'] = b64encode(os.urandom(10)).decode('utf-8')
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

@bp.route('/dashboard')
@login_required
def dashboard():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if jamlaApp.has_connected('gocardless'):
        gocardless_connected = True
    else:
        gocardless_connected = False
    if jamlaApp.has_connected('stripe'):
        stripe_connected = True
    else:
        stripe_connected = False
    return render_template('dashboard.html', jamla=jamla,
                           gocardless_connected=gocardless_connected,
                           stripe_connected=stripe_connected)

@bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_jamla():
    return render_template('formarraybasic/index.html')

@bp.route('/jamla', methods=['GET'])
@bp.route('/api/jamla', methods=['GET'])
@login_required
def fetch_jamla():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    #Strip out private values TODO don't store them here, move to .env?
    jamla['payment_providers'] = None
    resp = dict(items=jamla['items'], company=jamla['company'], name="fred", email='me@example.com')
    return jsonify(resp)

@bp.route('/connect/stripe', methods=['GET'])
@login_required
def connect_stripe():
    return "Connect Stripe."

@bp.route('/connect/stripe/manually', methods=['GET', 'POST'])
@login_required
def connect_stripe_manually():
    form = StripeConnectForm()
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if jamlaApp.has_connected('stripe'):
        stripe_connected = True
    else:
        stripe_connected = False
    if form.validate_on_submit():
        publishable_key = form.data['publishable_key']
        secret_key = form.data['secret_key']
        jamla['payment_providers']['stripe']['publishable_key'] = publishable_key
        jamla['payment_providers']['stripe']['secret_key'] = secret_key
        # Overwrite jamla file with gocardless access_token
        fp = open(current_app.config['JAMLA_PATH'], 'w')
        yaml.safe_dump(jamla,fp , default_flow_style=False)
        session['stripe_publishable_key'] = publishable_key
        # Set stripe public key JS
        return redirect(url_for('views.dashboard'))
    else:
        return render_template('connect_stripe_manually.html', form=form,
                jamla=jamla, stripe_connected=stripe_connected)

@bp.route('/connect/gocardless/manually', methods=['GET', 'POST'])
@login_required
def connect_gocardless_manually():
    form = GocardlessConnectForm()
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    if jamlaApp.has_connected('gocardless'):
        gocardless_connected = True
    else:
        gocardless_connected = False
    if form.validate_on_submit():
        access_token = form.data['access_token']
        jamla['payment_providers']['gocardless']['access_token'] = access_token
        # Check if live or test api key was given
        if "live" in access_token:
            jamla['payment_providers']['gocardless']['environment'] = 'live'
        else:
            jamla['payment_providers']['gocardless']['environment'] = 'sandbox'

        fp = open(current_app.config['JAMLA_PATH'], 'w')
        # Overwrite jamla file with gocardless access_token
        yaml.safe_dump(jamla,fp , default_flow_style=False)
        # Set users current session to store access_token for instant access
        session['gocardless_access_token'] = access_token
        return redirect(url_for('views.dashboard'))
    else:
        return render_template('connect_gocardless_manually.html', form=form,
                jamla=jamla, gocardless_connected=gocardless_connected)

@bp.route('/connect/gocardless', methods=['GET'])
@login_required
def connect_gocardless_start():
    flow = OAuth2WebServerFlow(
        client_id=current_app.config['GOCARDLESS_CLIENT_ID'],
        client_secret=current_app.config['GOCARDLESS_CLIENT_SECRET'],
        scope="read_write",
        redirect_uri="http://127.0.0.1:5000/connect/gocardless/oauth/complete",
        auth_uri="https://connect-sandbox.gocardless.com/oauth/authorize",
        token_uri="https://connect-sandbox.gocardless.com/oauth/access_token",
        initial_view="signup",
        prefill={
            "email": "tim@gocardless.com",
            "given_name": "Tim",
            "family_name": "Rogers",
            "organisation_name": "Tim's Fishing Store"
        }
    )
    authorize_url = flow.step1_get_authorize_url()
    return flask.redirect(authorize_url, code=302)

@bp.route('/connect/gocardless/oauth/complete', methods=['GET'])
@login_required
def gocardless_oauth_complete():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    flow = OAuth2WebServerFlow(
            client_id=current_app.config['GOCARDLESS_CLIENT_ID'],
            client_secret=current_app.config['GOCARDLESS_CLIENT_SECRET'],
            scope="read_write",
            # You'll need to use exactly the same redirect URI as in the last step
            redirect_uri="http://127.0.0.1:5000/connect/gocardless/oauth/complete",
            auth_uri="https://connect-sandbox.gocardless.com/oauth/authorize",
            token_uri="https://connect-sandbox.gocardless.com/oauth/access_token",
            initial_view="signup"
    )
    access_token = flow.step2_exchange(request.args.get('code'))

    jamla['payment_providers']['gocardless']['access_token'] = access_token.access_token
    fp = open(current_app.config['JAMLA_PATH'], 'w')
    # Overwrite jamla file with gocardless access_token
    yaml.safe_dump(jamla,fp , default_flow_style=False)
    # Set users current session to store access_token for instant access
    session['gocardless_access_token'] = access_token.access_token
    session['gocardless_organisation_id'] = access_token.token_response['organisation_id']

    return redirect(url_for('views.dashboard'))

@bp.route('/push-mandates', methods=['GET'])
def push_mandates():
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    gocclient = gocardless_pro.Client(
        access_token = get_secret('gocardless', 'access_token', jamla),
        environment = jamla['payment_providers']['gocardless']['environment']
    )
    #Loop mandates
    for mandate in gocclient.mandates.list().records:
        print "##"
        # Push to Penguin
        print "Pushing mandate to penguin.."
        title = mandate.id
        fields = {
            'title':title,
            'field_gocardless_created_at': mandate.created_at,
            'field_gocardless_cust_bank_id': mandate.attributes['links']['customer_bank_account'],
            'field_gocardless_mandate_creditr': mandate.attributes['links']['creditor'],
            'field_gocardless_mandate_cust_id': mandate.attributes['links']['customer'],
            'field_gocardless_mandate_id': mandate.id,
            'field_gocardless_mandate_ref': mandate.reference,
            'field_gocardless_mandate_scheme': mandate.scheme,
            'field_gocardless_mandate_status': mandate.status,
            'field_gocardless_metadata' : str(mandate.metadata),
            'field_gocardless_new_mandate_id': '',
            'field_gocardless_pmts_req_approv': mandate.payments_require_approval,
            'field_gocardless_next_pos_charge': mandate.next_possible_charge_date
        }
        Rest.post(entity='mandate', fields=fields)
    return "Mandates pushed"

@bp.route('/push-payments', methods=['GET'])
def push_payments():
    """
    Push payments to Penguin.
    Assume a gocardless endpoint for now.
    """
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=jamla)
    gocclient = gocardless_pro.Client(
        access_token = get_secret('gocardless', 'access_token'),
        environment= jamla['payment_providers']['gocardless']['environment']
    )
    #Loop customers
    for payments in gocclient.payments.list().records:
        ##Loop each payment within payment response body
        response = payments.api_response.body
        for payment in response['payments']:
            print payment
            print payment['status']
            print "##"
            # Push to Penguin
            print "Creating transaction to penguin.."
            title = "a transaction title"
            try:
                payout_id = payment['links']['payout']
            except:
                payout_id = None
            fields = {
                'title':title,
                'field_gocardless_payment_id': payment['id'],
                'field_gocardless_payout_id': payout_id,
                'field_gocardless_amount': payment['amount'],
                'field_gocardless_payment_status': payment['status'],
                'field_mandate_id': payment['links']['mandate'],
                'field_gocardless_subscription_id': payment['links']['subscription'],
                'field_gocardless_amount_refunded': payment['amount_refunded'],
                'field_gocardless_charge_date': payment['charge_date'],
                'field_gocardless_created_at' : payment['created_at'],
                'field_gocardless_creditor_id': payment['links']['creditor']
            }
            Rest.post(entity='transaction', fields=fields)

    return "Payments have been pushed"

@bp.route('/retry-payment/<payment_id>', methods=['GET'])
def retry_payment(payment_id):
    jamla = get_jamla()
    jamlaapp = jamla()
    jamlaapp.load(jamla=jamla)
    gocclient = gocardless_pro.Client(
        access_token = get_secret('gocardless', 'access_token'),
        environment = jamla['payment_providers']['gocardless']['environment']
    )
    r = gocclient.payments.retry(payment_id)

    return "Payment (" + payment_id + " retried." + str(r)

def getItem(container, i, default=None):
    try:
        return container[i]
    except IndexError:
        return default
