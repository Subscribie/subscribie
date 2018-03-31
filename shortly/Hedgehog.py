import os,sys
sys.path.append('../../../modules')
import random
from os import environ
from base64 import b64encode
import requests
import time
from bs4 import BeautifulSoup
import gocardless_pro
import sqlite3
import smtplib
from penguin_rest import Decorators
from jamla import Jamla
import sendgrid
from sendgrid.helpers.mail import *
from flask import Flask, render_template, session, redirect, url_for, escape, request
import flask
import jinja2
import datetime
from penguin_rest import Rest

class MyFlask(flask.Flask):

    def __init__(self, import_name):
        super(MyFlask, self).__init__(import_name)

alphanum = "abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRTUVWXYZ0123456789"

app = MyFlask(__name__)
with app.app_context():
    app.config.from_pyfile('.env')
    app.secret_key = app.config['SECRET_KEY']
    with app.app_context():
        from flask import g
        jamla = getattr(g, 'jamla', None)
        if jamla is None:
            jamla = Jamla.load(app.config['JAMLA_PATH'])
    my_loader = jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(app.config['TEMPLATE_FOLDER']),
                app.jinja_loader,
            ])
    app.jinja_loader = my_loader
    app.static_folder = app.config['STATIC_FOLDER']

    @app.route('/', methods=['GET'])
    def choose():
        session['sid'] = b64encode(''.join([alphanum[random.randint(0, len(alphanum) - 1)] for _ in range(0, 24)])).decode('utf-8')
        return render_template('choose.html', jamla=jamla)

# Register yml pages as routes & import any custom modules they depend on
    for i,v in enumerate(jamla['pages']):
        path = jamla['pages'][i][jamla['pages'][i].keys()[0]]['path']
        template_file = jamla['pages'][i][jamla['pages'][i].keys()[0]]['template_file']
        view_func_name = jamla['pages'][i].keys()[0]
        ##Generate view function
        generate_view_func = """def %s_view_func():
        return render_template('%s', jamla=jamla)""" % (view_func_name, template_file)
        exec(generate_view_func)
        method_name = view_func_name + "_view_func"
        possibles = globals().copy()
        possibles.update(locals())
        view_func = possibles.get(method_name)
        app.add_url_rule("/" + path, view_func_name + '_view_func', view_func)
        ## Import custom modules if page has them
        if 'depends' in jamla['pages'][i][jamla['pages'][i].keys()[0]]:
            for moduleName in jamla['pages'][i][jamla['pages'][i].keys()[0]]['depends']:
                print moduleName + " is the module name."
                __import__(moduleName)



    def sku_exists(sku):
        for item in jamla['items']:
            if item['sku'] == str(sku):
                return True
        return False 
    def sku_get_index(sku):
        for index,v in enumerate(jamla['items']):
            if jamla['items'][index]['sku'] == str(sku):
                return index
        return False

    def sku_get_title(sku):
        index = sku_get_index(sku)
        title  = jamla['items'][index]['title']
        return title
        
    def sku_get_monthly_price(sku):
        price = jamla['items'][sku_get_index(sku)]['monthly_price']
        return price


    @app.route('/new_customer', methods=['GET'])
    def new_customer():
        package = request.args.get('plan','not set')
        return render_template('new_customer.html', jamla=jamla, package=package)

    @app.route('/new_customer', methods=['POST'])
    @Decorators.create_partner
    @Decorators.create_contact
    @Decorators.attach_contact_partner
    def store_customer():
        given_name = request.form['given_name']
        family_name = request.form['family_name']
        address_line1 = request.form['address_line1']
        city = request.form['city']
        postal_code = request.form['postal_code']
        email = request.form['email']
        mobile = request.form['mobile']
        now = datetime.datetime.now()
        # Store customer in session
        sid = session['sid']

        # Store plan in session
        if sku_exists(request.args.get('plan')):
            wants = request.args.get('plan')
            session['plan'] = wants
        print "##################"
        con = sqlite3.connect(app.config["DB_FULL_PATH"])
        cur = con.cursor()
        cur.execute("INSERT INTO person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (sid, now, given_name, family_name, address_line1, city, postal_code, email, mobile, wants, 'null', 'null', False))
        con.commit()
        cur.execute("SELECT * FROM person")
        print cur.fetchone()
        con.close()
        #redirect to Crab with sid in the query
        return redirect(app.config["CRAB_URL"] + '?sid=' + sid + '&package=' + wants + '&fname=' + given_name)

    @app.route('/sign', methods=['GET'])
    def on_sign(self,request):
        return self.render_template('signature.html')

    @app.route('/establish_mandate', methods=['GET'])
    def establish_mandate():
        #lookup the customer with sid and get their relevant details
        sid = session['sid']
        con = sqlite3.connect(app.config["DB_FULL_PATH"])
        cur = con.cursor()
        cur.execute("SELECT * FROM person p WHERE p.sid = ?", (sid,))
        res = cur.fetchone()
        print res
        con.close()

        if res:
            # validate that hasInstantPaid is true for the customer
            if res[12] == True:
                gocclient = gocardless_pro.Client(
                    access_token = app.config['GOCARDLESS_TOKEN'],
                    environment= app.config['GOCARDLESS_ENVIRONMENT']
                )
                redirect_flow = gocclient.redirect_flows.create(
                    params = {
                        "description" : "Karma Computing Broadband",
                        "session_token" : sid,
                        "success_redirect_url" : app.config['SUCCESS_REDIRECT_URL'],
                        "prefilled_customer" : {
                            "given_name" : res[2],
                            "family_name": res[3],
                            "address_line1": res[4],
                            "city" : res[5],
                            "postal_code": res[6],
                            "email": res[7]
                        }
                    }
                )
                # Hold on to this ID - we'll need it when we
                # "confirm" the dedirect flow later
                print("ID: {} ".format(redirect_flow.id))
                print("URL: {} ".format(redirect_flow.redirect_url))
                return redirect(redirect_flow.redirect_url)
            else:
                print "hasInstantPaid on this customer was false"
                #TODO: respond with 403
        else:
            print "no customer found with sid"
            #TODO: respond with 400

    @app.route('/complete_mandate', methods=['GET'])
    def on_complete_mandate():
        redirect_flow_id = request.args.get('redirect_flow_id')
        print("Recieved flow ID: {} ".format(redirect_flow_id))

        gocclient = gocardless_pro.Client(
            access_token = app.config['GOCARDLESS_TOKEN'],
            environment= app.config['GOCARDLESS_ENVIRONMENT']
        )

        redirect_flow = gocclient.redirect_flows.complete(
            redirect_flow_id,
            params = {
                "session_token": session['sid']
        })
        # Save this mandate & customer ID for the next section.
        print ("Mandate: {}".format(redirect_flow.links.mandate))
        print ("Customer: {}".format(redirect_flow.links.customer))
        session['gocardless_mandate_id'] = redirect_flow.links.mandate
        session['gocardless_customer_id'] = redirect_flow.links.customer
        # Update Partner record with Gocardless Mandate & Customer Id
        fields = {
            'field_gocardless_mandate_id': session['gocardless_mandate_id'],
            'field_gocardless_customer_id':session['gocardless_customer_id']
        }
        Rest.patch(session['partner_nid'], 'partner', fields, embeded=False) 

        # Store customer
        sid = session['sid']
        now = datetime.datetime.now()
        mandate = redirect_flow.links.mandate
        customer = redirect_flow.links.customer
        flow = redirect_flow_id

        con = sqlite3.connect(app.config['DB_FULL_PATH'])
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
        currentDate = datetime.datetime.now()
        goLive = currentDate + datetime.timedelta(days = 15)

        # Create subscription
        gocclient.subscriptions.create(params={
            "amount":sku_get_monthly_price(session['plan']),
            "currency":"GBP",
            "name": sku_get_title(session['plan']),
            "interval_unit": "monthly",
            "metadata": {
                "sku":session['plan']
            },
            "links": {
                "mandate":session['gocardless_mandate_id']
            }
        })

        #TODO loop over Jamla items vs chosenPackage to work out contractExpiry, monthlycost, lead_time
        contractExpiry = goLive + datetime.timedelta(days = 365)
        monthlyCost = "As quoted"
        goLive = "ASAP"

        ## ADMIN
        try:
            sg = sendgrid.SendGridAPIClient(apikey=app.config['SENDGRID_API_KEY'])
            from_email = Email("broadband@karmacomputing.co.uk", "BB ORDER")
            to_email = Email("broadband@karmacomputing.co.uk")
            subject = "NEW BROABDAND ORDER"
            content = Content("text/html", "There has been an error constructing this email.")
            mail = Mail(from_email, subject, to_email, content)
            mail.personalizations[0].add_substitution(Substitution("-customerName-", customerName))
            mail.personalizations[0].add_substitution(Substitution("-customerPhone-", customerPhone))
            mail.personalizations[0].add_substitution(Substitution("-customerAddress-", customerAddress))
            mail.personalizations[0].add_substitution(Substitution("-customerEmail-", customerEmail))
            mail.personalizations[0].add_substitution(Substitution("-broadbandPackage-", chosenPackage))
            mail.personalizations[0].add_substitution(Substitution("-customerExistingLine-", customerExistingLine))
            mail.personalizations[0].add_substitution(Substitution("-customerExistingNumber-", customerExistingNumber))
            mail.template_id = "8b49f623-9368-4cf6-94c1-53cc2f429b9b"
            response = sg.client.mail.send.post(request_body=mail.get())

            ## CUSTOMER
            from_email = Email("broadband@karmacomputing.co.uk", "Karma Broadband Team")
            to_email = Email(customerEmail)
            mail = Mail(from_email, subject, to_email, content)
            mail.personalizations[0].add_substitution(Substitution("-name-", customerName))
            mail.personalizations[0].add_substitution(Substitution("-package-", chosenPackage))
            mail.personalizations[0].add_substitution(Substitution("-contractExpiry-", contractExpiry))
            mail.personalizations[0].add_substitution(Substitution("-goLive-", goLive))
            mail.personalizations[0].add_substitution(Substitution("-monthlyCost-", monthlyCost))
            mail.template_id = "0c383660-2801-4448-b3cf-9bb608de9ec7"
            response = sg.client.mail.send.post(request_body=mail.get())
        except Exception:
            pass

        # Display a confirmation page to the customer, telling them
        # their Direct Debit has been set up. You could build your own,
        # or use ours, which shows all the relevant information and is
        # translated into all the languages we support.
        print("Confirmation URL: {}".format(redirect_flow.confirmation_url))
        return redirect(app.config['THANKYOU_URL'])

    @app.route('/thankyou', methods=['GET'])
    def thankyou():
        print "##### The partner nid is:" + str(session['partner_nid'])
        print "##### The Mandate id is:" + str(session['gocardless_mandate_id'])
        print "##### The GC Customer id is: " + str(session['gocardless_customer_id'])
        return render_template('thankyou.html', jamla=jamla)

    @app.route('/broadband_availability_postcode_checker')
    def broadband_availability_postcode_checker():
        return render_template('broadband-availability-postcode-checker.html')

    @app.route('/gettingstarted', methods=['GET'])
    def on_gettingstarted():
        return render_template('gettingstarted.html')

    @app.route('/prerequisites', methods=['GET'])
    def on_prerequisites():
        """
        Render template with mandatory questions for a
        sucessful onboarding e.g. "Do you already have
        a x,y,z?".
        """
        return render_template('prerequisites.html')

    @app.route('/push-mandates', methods=['GET'])
    def push_mandates():
        gocclient = gocardless_pro.Client(
            access_token = app.config['GOCARDLESS_TOKEN'],
            environment= app.config['GOCARDLESS_ENVIRONMENT']
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

    @app.route('/push-payments', methods=['GET'])
    def push_payments():
        """
        Push payments to Penguin.
        Assume a gocardless endpoint for now.
        """
        gocclient = gocardless_pro.Client(
            access_token = app.config['GOCARDLESS_TOKEN'],
            environment= app.config['GOCARDLESS_ENVIRONMENT']
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

    @app.route('/retry-payment/<payment_id>', methods=['GET'])
    def retry_payment(payment_id):
        gocclient = gocardless_pro.Client(
            access_token = app.config['GOCARDLESS_TOKEN'],
            environment= app.config['GOCARDLESS_ENVIRONMENT']
        )
        r = gocclient.payments.retry(payment_id)

        return "Payment (" + payment_id + " retried." + str(r)

application = app
