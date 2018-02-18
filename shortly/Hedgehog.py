import os
from os import environ
from base64 import b64encode
import requests
import time
from bs4 import BeautifulSoup
import gocardless_pro
import sqlite3
import smtplib
from penguin_rest import Rest
from jamla import Jamla
import sendgrid
from sendgrid.helpers.mail import *
from flask import Flask, render_template, session, redirect, url_for, escape, request
import datetime

app = Flask(__name__)
app.config.from_pyfile('.env')
app.secret_key = app.config['SECRET_KEY']
with app.app_context():
    from flask import g
    jamla = getattr(g, 'jamla', None)
    if jamla is None:
        jamla = Jamla.load(app.config['JAMLA_PATH'])

@app.route('/', methods=['POST'])
def result():
    buildingnumber = request.form['buildingnumber']
    PostCode = request.form['PostCode']
    now = datetime.datetime.now()
    prettyTime = datetime.datetime.now().strftime("%H:%M %D")
    sid = request.cookies.get('karma_cookie')
    print app.config['DB_FULL_PATH']
    con = sqlite3.connect(app.config['DB_FULL_PATH'])
    cur = con.cursor()
    cur.execute("INSERT INTO lookups VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (sid, now, buildingnumber, '', '', '', '', PostCode))
    con.commit()
    cur.execute("SELECT * FROM lookups")
    print cur.fetchone()
    con.close()
    canADSL = False
    canFibre = False
    nophone = False
    if not is_valid_lookup(request.form):
        error = 'Please enter a valid request'
    else:
        r = requests.post('https://www.dslchecker.bt.com/adsl/ADSLChecker.AddressOutput',
                         data = {'buildingnumber': request.form['buildingnumber'],
                               'postCode': request.form['PostCode']})
        result = r.text
        soup = BeautifulSoup(r.text, 'html.parser')
        soup.prettify()
        soup.find_all('span')
        result = {}
        result['VDSL Range A'] = {'Downstream': {'high':'', 'low':''},'Upstream': {'high':'', 'low':''}}
        result['WBC ADSL 2+'] = {'Downstream': '','Upstream': ''}
        result['WBC ADSL 2+ Annex M'] = {'Downstream': '','Upstream': ''}
        result['ADSL Max'] = {'Downstream': '','Upstream': ''}


        for span in soup.find_all('span'):
            if "VDSL Range A (Clean)" in span:
                for index, child in enumerate(span.parent.parent.children):
                    #print index, child
                    if index == 3:
                        result['VDSL Range A']['Downstream']['high'] = child.text
                        try:
                            float(child.text)
                            canFibre = True
                        except ValueError as verr:
                            canFibre = False
                    if index == 5:
                        result['VDSL Range A']['Downstream']['low'] = child.text
                        try:
                            float(child.text)
                            canFibre = True
                        except ValueError as verr:
                            canFibre = False
                    if index == 7:
                       result['VDSL Range A']['Upstream']['high'] = child.text
                    if index == 9:
                       result['VDSL Range A']['Upstream']['low'] = child.text

            if "WBC ADSL 2+" in span:
                for index, child in enumerate(span.parent.parent.children):
                    print index, child
                    if index == 3:
                        result['WBC ADSL 2+']['Downstream'] = child.text.replace('Up to ','')
                        try:
                            float(child.text.replace('Up to ',''))
                            canADSL = True
                        except ValueError as verr:
                            canADSL = False
                    if index == 5:
                        result['WBC ADSL 2+']['Upstream'] = child.text.replace('Up to ','')
                        if result['WBC ADSL 2+']['Upstream'].find("--") != -1:
                                result['WBC ADSL 2+']['Upstream'] = ""

            if "WBC ADSL 2+ Annex M" in span:
                for index, child in enumerate(span.parent.parent.children):
                    print index, child
                    if index == 3:
                        result['WBC ADSL 2+ Annex M']['Downstream'] = child.text.replace('Up to ','')
                        try:
                            float(child.text.replace('Up to ',''))
                            canADSL = True
                        except ValueError as verr:
                            canADSL = False
                    if index == 5:
                        result['WBC ADSL 2+ Annex M']['Upstream'] = child.text.replace('Up to ','')
                        if result['WBC ADSL 2+ Annex M']['Upstream'].find("--") != -1:
                                result['WBC ADSL 2+ Annex M']['Upstream'] = ""

            if "ADSL Max" in span:
                for index, child in enumerate(span.parent.parent.children):
                    print index, child
                    if index == 3:
                        result['ADSL Max']['Downstream'] = child.text.replace('Up to ','')
                        try:
                            float(child.text.replace('Up to ',''))
                            canADSL = True
                        except ValueError as verr:
                            canADSL = False
                    if index == 5:
                        result['ADSL Max']['Upstream'] = child.text.replace('Up to ','')
                        if result['ADSL Max']['Upstream'].find("--") != -1:
                                result['ADSL Max']['Upstream'] = ""

        try:
            if request.cookies.get('nophone'):
                nophone=True
        except  KeyError:
            pass
        uptoSpeedFibre = result['VDSL Range A']['Downstream']['high']
        uptoSpeedADSL = result['WBC ADSL 2+']['Downstream']

        fields = {'title':time.time(),
              'field_building_number':request.form['buildingnumber'],
              'field_postcode_availability':request.form['PostCode'],
              'field_vdsl_a_clean_mbps_high_dl':result['VDSL Range A']['Downstream']['high'],
              'field_vdsl_a_clean_mbps_low_dl':result['VDSL Range A']['Downstream']['low'],
              'field_vdsl_a_clean_mbps_high_ul':result['VDSL Range A']['Upstream']['high'],
              'field_vdsl_a_clean_mbps_low_ul': result['VDSL Range A']['Upstream']['low'],
              'field_adsl_2_downstream': result['WBC ADSL 2+']['Downstream'],
              'field_adsl_2_upstream': result['WBC ADSL 2+']['Upstream'],
              'field_adsl_2_annex_m_downstream': result['WBC ADSL 2+ Annex M']['Downstream'],
              'field_adsl_2_annex_m_upstream': result['WBC ADSL 2+ Annex M']['Upstream'],
              'field_adsl_max_downstream': result['ADSL Max']['Downstream'],
              'field_adsl_max_upstream': result['ADSL Max']['Upstream']}
        Rest.post(entity='broadband_availability_lookup', fields=fields)

    return render_template('result.html', jamla=jamla, result=result, canADSL=canADSL, canFibre=canFibre, buildingnumber=buildingnumber, postCode=PostCode, now=prettyTime, nophone=nophone)


@app.route('/', methods=['GET'])
def start():
    session['sid'] = b64encode(os.urandom(24)).decode('utf-8')
    error = None
    nophone = False
    try:
        if request.cookies.get('nophone'):
            nophone=True
    except  KeyError:
        pass
    result = ''
    return render_template('start.html', error=error, cheese=True, nophone=nophone)

def is_valid_lookup(form):
    return True


@app.route('/new_customer', methods=['GET'])
def new_customer():
    package = request.args.get('plan','not set')
    return render_template('new_customer.html', package=package)

@app.route('/new_customer', methods=['POST'])
def store_customer():
    given_name = request.form['given_name']
    family_name = request.form['family_name']
    address_line1 = request.form['address_line1']
    city = request.form['city']
    postal_code = request.form['postal_code']
    email = request.form['email']
    mobile = request.form['mobile']
    now = datetime.datetime.now()
    wants = request.args.get('plan')
    # Store customer
    sid = session['sid'] 
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
    print ("Mandate: {}".format(redirect_flow.links.mandate))
    # Save this mandate ID for the next section.
    print ("Customer: {}".format(redirect_flow.links.customer))

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
    broadbandPackage = row[9]
    customerExistingLine = row[10]
    customerExistingNumber = row[11]
    currentDate = datetime.datetime.now()
    goLive = currentDate + datetime.timedelta(days = 15)

    if broadbandPackage == "adsl":
        broadbandPackage = "ADSL 2+"
        contractExpiry = goLive + datetime.timedelta(days = 90)
        monthlyCost = "34.99"
    elif broadbandPackage == "fibre":
        broadbandPackage = "FTTC 40:10"
        contractExpiry = goLive + datetime.timedelta(days = 365)
        monthlyCost = "41.99"
    elif broadbandPackage == "fibre_plus":
        broadbandPackage = "FTTC 80:20"
        contractExpiry = goLive + datetime.timedelta(days = 365)
        monthlyCost = "41.99"

    contractExpiry = contractExpiry.strftime('%d/%m/%Y') + "*"
    goLive = goLive.strftime('%d/%m/%Y')

    ## ADMIN
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
    mail.personalizations[0].add_substitution(Substitution("-broadbandPackage-", broadbandPackage))
    mail.personalizations[0].add_substitution(Substitution("-customerExistingLine-", customerExistingLine))
    mail.personalizations[0].add_substitution(Substitution("-customerExistingNumber-", customerExistingNumber))
    mail.template_id = "8b49f623-9368-4cf6-94c1-53cc2f429b9b"
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except urllib.HTTPError as e:
        print (e.read())
        exit()
    print(response.status_code)
    print(response.body)
    print(response.headers)

    ## CUSTOMER
    from_email = Email("broadband@karmacomputing.co.uk", "Karma Broadband Team")
    to_email = Email(customerEmail)
    mail = Mail(from_email, subject, to_email, content)
    mail.personalizations[0].add_substitution(Substitution("-name-", customerName))
    mail.personalizations[0].add_substitution(Substitution("-package-", broadbandPackage))
    mail.personalizations[0].add_substitution(Substitution("-contractExpiry-", contractExpiry))
    mail.personalizations[0].add_substitution(Substitution("-goLive-", goLive))
    mail.personalizations[0].add_substitution(Substitution("-monthlyCost-", monthlyCost))
    mail.template_id = "0c383660-2801-4448-b3cf-9bb608de9ec7"
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except urllib.HTTPError as e:
        print (e.read())
        exit()
    print(response.status_code)
    print(response.body)
    print(response.headers)

    # Display a confirmation page to the customer, telling them
    # their Direct Debit has been set up. You could build your own,
    # or use ours, which shows all the relevant information and is
    # translated into all the languages we support.
    print("Confirmation URL: {}".format(redirect_flow.confirmation_url))
    return redirect(app.config['THANKYOU_URL'])

@app.route('/thankyou', methods=['GET'])
def thankyou():
    return render_template('thankyou.html')

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

application = app
