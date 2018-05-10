import os
import yaml
import datetime
import random
import sqlite3
import smtplib                                                                   
import flask_login
from hedgehog import app, Jamla, session, render_template, \
     request, redirect, alphanum, CustomerForm, LoginForm, gocardless_pro, \
     journey_complete, GocardlessConnectForm, StripeConnectForm, current_app, \
     redirect, url_for, StripeConnectForm
from .User import User, send_login_url
from base64 import b64encode, urlsafe_b64encode 

jamlaApp = Jamla()                                                               
jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])

@app.route('/')                                                 
def choose():
    session['sid'] = b64encode(''.join([alphanum[random.randint(0, len(alphanum) - 1)] for _ in range(0, 24)])).decode('utf-8')
    return render_template('choose.html', jamla=jamla)

@app.route('/new_customer', methods=['GET'])                                     
def new_customer():                                                              
    package = request.args.get('plan','not set')                                 
    form = CustomerForm()                                                        
    return render_template('new_customer.html', jamla=jamla, form=form, package=package)

@app.route('/new_customer', methods=['POST'])                                    
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
                                                                                 
        # Store plan in session                                                  
	jamlaApp = Jamla()                                                               
	jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
        if jamlaApp.sku_exists(request.args.get('plan')):                                 
            wants = request.args.get('plan')                                     
            session['plan'] = wants                                              
        print "##################"                                               
        con = sqlite3.connect(app.config["DB_FULL_PATH"])                        
        cur = con.cursor()                                                       
        cur.execute("INSERT INTO person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (sid, now, given_name, family_name,
                    address_line_one, city, postcode, email, mobile,             
                    wants, 'null', 'null', False))                               
        con.commit()                                                             
        con.close()                                                              
        #redirect to Crab with sid in the query                                  
        return redirect(app.config["CRAB_URL"] + '?sid=' + sid + '&package=' + wants + '&fname=' + given_name)
    else:                                                                        
        return "Invalid form"

@app.route('/establish_mandate', methods=['GET'])                                
def establish_mandate():
    jamlaApp = Jamla()
    jamla = jamlaApp.load(app.config['JAMLA_PATH'])
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
                access_token = jamlaApp.get_secret('gocardless', 'access_token'),  
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
    jamlaApp = Jamla()
    jamla = jamlaApp.load(app.config['JAMLA_PATH'])
    redirect_flow_id = request.args.get('redirect_flow_id')                      
    print("Recieved flow ID: {} ".format(redirect_flow_id))                      
                                                                                 
    gocclient = gocardless_pro.Client(                                           
        access_token = jamlaApp.get_secret('gocardless', 'access_token'),          
        environment= app.config['GOCARDLESS_ENVIRONMENT']                        
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
    except Exception as e:                                                       
        if isinstance(e, gocardless_pro.errors.InvalidStateError):               
            if e.error['type'] == 'invalid_state':                               
                # Allow pass through if redirect flow already completed          
                if e.errors[0]['reason'] == "redirect_flow_already_completed":   
                    pass                                                         
    # Display a confirmation page to the customer, telling them                  
    # their Direct Debit has been set up.
    return redirect(app.config['THANKYOU_URL'])

@app.route('/thankyou', methods=['GET'])                                         
def thankyou():
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

@app.route('/login/<login_token>', methods=['GET'])                              
def validate_login(login_token):                                                 
    if len(login_token) < 10:                                                    
        return 'Invalid token'                                                   
    # Try to get email from login_token                                          
    con = sqlite3.connect(app.config["DB_FULL_PATH"])                            
    con.row_factory = sqlite3.Row # Dict based result set                        
    cur = con.cursor()                                                           
    cur.execute('SELECT email FROM user WHERE login_token=?', (login_token,))    
    result = cur.fetchone()                                                      
    con.close()                                                                  
    if result is None:                                                           
        return "Invalid token"                                                   
    # Invaldate previous token                                                   
    new_login_token = urlsafe_b64encode(os.urandom(24))                          
    con = sqlite3.connect(app.config["DB_FULL_PATH"])                            
    cur = con.cursor()                                                           
    cur.execute('UPDATE user SET login_token=? WHERE login_token=?', (new_login_token, login_token,))
    con.commit()                                                                 
    con.close()                                                                  
                                                                                 
    email = result['email']                                                      
    user = User()                                                                
    user.id = email                                                              
    flask_login.login_user(user)                                                 
    return redirect(url_for('protected'))                                        
                                                                                 
    return "Code is %s" % login_token;

@app.route('/logout')                                                            
def logout():                                                                    
    flask_login.logout_user()                                                    
    return 'Logged out'                                                          
                                                                                 
@app.route('/dashboard')                                                         
@flask_login.login_required                                                      
def dashboard():                                                                 
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
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
                                                                                 
@app.route('/protected')                                                         
@flask_login.login_required                                                      
def protected():                                                                 
    return redirect(url_for('dashboard'));

@app.route('/login', methods=['POST'])                                           
def generate_login_token():                                                      
    form = LoginForm()                                                           
    if form.validate_on_submit():                                                
        try:
            send_login_url(form.data['email'])
            return ("Check your email")                                          
        except Exception as e:                                                        
            print e
            return ("Failed to generate login email.")
@app.route('/login', methods=['GET'])                                            
def login():                                                                     
    form = LoginForm()                                                           
    return render_template('login.html', form=form, jamla=jamla)                 
                                                                                 
@app.route('/connect/stripe', methods=['GET'])                                   
@flask_login.login_required                                                      
def connect_stripe():                                                            
    return "Connect Stripe."

@app.route('/connect/stripe/manually', methods=['GET', 'POST'])                  
@flask_login.login_required                                                      
def connect_stripe_manually():                                                   
    form = StripeConnectForm()                                                   
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
    if form.validate_on_submit():                                                
        publishable_key = form.data['publishable_key']                           
        secret_key = form.data['secret_key']                                     
        jamla['payment_providers']['stripe']['publishable_key'] = publishable_key
        jamla['payment_providers']['stripe']['secret_key'] = secret_key          
        fp = open(app.config['JAMLA_PATH'], 'w')                                 
        # Overwrite jamla file with gocardless access_token                                                              
        yaml.safe_dump(jamla,fp , default_flow_style=False)                      
        flask_login.current_user.stripe_publishable_key = publishable_key        
        # Set Crab JS                                                            
        fp = open(app.config['CRAB_PATH'] + 'js_env/STRIPE_PUBLIC_KEY.env', 'w') 
        fp.write(publishable_key)                                                
        fp.close()                                                               
        return redirect(url_for('dashboard'))                                    
    else:                                                                        
        return render_template('connect_stripe_manually.html', form=form,        
                jamla=jamla)

@app.route('/connect/gocardless/manually', methods=['GET', 'POST'])              
@flask_login.login_required                                                      
def connect_gocardless_manually():                                               
    form = GocardlessConnectForm()                                               
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
    if form.validate_on_submit():                                                
        access_token = form.data['access_token']                                 
        jamla['payment_providers']['gocardless']['access_token'] = access_token  
        fp = open(app.config['JAMLA_PATH'], 'w')                                 
        # Overwrite jamla file with gocardless access_token                                                              
        yaml.safe_dump(jamla,fp , default_flow_style=False)                      
        # Set users current session to store access_token for instant access     
        flask_login.current_user.gocardless_access_token = access_token          
        return form.data['access_token']                                         
    else:                                                                        
        return render_template('connect_gocardless_manually.html', form=form,    
                jamla=jamla)

@app.route('/connect/gocardless', methods=['GET'])                               
@flask_login.login_required                                                      
def connect_gocardless_start():                                                  
    flow = OAuth2WebServerFlow(                                                  
        client_id=app.config['GOCARDLESS_CLIENT_ID'],                            
        client_secret=app.config['GOCARDLESS_CLIENT_SECRET'],                    
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

@app.route('/connect/gocardless/oauth/complete', methods=['GET'])                
@flask_login.login_required                                                      
def gocardless_oauth_complete():                                                 
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
    flow = OAuth2WebServerFlow(                                                  
            client_id=app.config['GOCARDLESS_CLIENT_ID'],                        
            client_secret=app.config['GOCARDLESS_CLIENT_SECRET'],                
            scope="read_write",                                                  
            # You'll need to use exactly the same redirect URI as in the last step
            redirect_uri="http://127.0.0.1:5000/connect/gocardless/oauth/complete",
            auth_uri="https://connect-sandbox.gocardless.com/oauth/authorize",   
            token_uri="https://connect-sandbox.gocardless.com/oauth/access_token",
            initial_view="signup"                                                
    )                                                                            
    access_token = flow.step2_exchange(request.args.get('code'))                 
                                                                                 
    jamla['payment_providers']['gocardless']['access_token'] = access_token.access_token
    fp = open(app.config['JAMLA_PATH'], 'w')                                     
    # Overwrite jamla file with gocardless access_token                                                              
    yaml.safe_dump(jamla,fp , default_flow_style=False)                          
    # Set users current session to store access_token for instant access         
    flask_login.current_user.gocardless_access_token = access_token.access_token 
    flask_login.current_user.gocardless_organisation_id = access_token.token_response['organisation_id']
                                                                                 
    return redirect(url_for('dashboard'))

@app.route('/push-mandates', methods=['GET'])                                    
def push_mandates():                                                             
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
    gocclient = gocardless_pro.Client(                                           
        access_token = get_secret('gocardless', 'access_token', jamla),          
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
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
    gocclient = gocardless_pro.Client(                                           
        access_token = get_secret('gocardless', 'access_token'),          
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
    jamlaApp = Jamla()                                                               
    jamla = jamlaApp.load(src=app.config['JAMLA_PATH'])
    gocclient = gocardless_pro.Client(                                           
        access_token = get_secret('gocardless', 'access_token'),          
        environment= app.config['GOCARDLESS_ENVIRONMENT']                        
    )                                                                            
    r = gocclient.payments.retry(payment_id)                                     
                                                                                 
    return "Payment (" + payment_id + " retried." + str(r) 
