from flask import Blueprint, render_template, abort, flash, json
from jinja2 import TemplateNotFound
from subscribie import Jamla, session, render_template, \
     request, redirect, gocardless_pro, \
     GocardlessConnectForm, StripeConnectForm, current_app, \
     redirect, url_for, GoogleTagManagerConnectForm, ItemsForm,\
     jsonify, TawkConnectForm
from subscribie.auth import login_required
from subscribie.db import get_jamla, get_db
import yaml
from flask_uploads import configure_uploads, UploadSet, IMAGES
import os


admin_theme = Blueprint('admin', __name__, template_folder='templates',
                        static_folder='static')

@admin_theme.route('/dashboard')                     
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
    return render_template('admin/dashboard.html', jamla=jamla,                        
                           gocardless_connected=gocardless_connected,            
                           stripe_connected=stripe_connected)

@admin_theme.route('/edit', methods=['GET', 'POST'])                                      
@login_required                                                                  
def edit_jamla():
    form = ItemsForm()
    jamla = get_jamla()
    if form.validate_on_submit():
        jamla['company']['name'] = request.form['company_name']
        jamla['users'][0] = request.form['email']
        # Loop items
        for index in request.form.getlist('itemIndex', type=int):
            # Get current values
            # Update
            jamla['items'][index]['title'] = getItem(form.title.data,index,default='').strip()
            jamla['items'][index]['requirements']['subscription'] = bool(getItem(form.subscription.data, index))
            jamla['items'][index]['monthly_price'] = int(getItem(form.monthly_price.data, index, default=0) * 100)
            jamla['items'][index]['requirements']['instant_payment'] = bool(getItem(form.instant_payment.data, index))
            jamla['items'][index]['sell_price'] = int(getItem(form.sell_price.data, index, default=0) * 100)
            jamla['items'][index]['selling_points'] = getItem(form.selling_points.data, index, default='')
            # Primary icon image storage
            f = getItem(form.image.data, index)
            if f:
                images = UploadSet('images', IMAGES)
                filename = images.save(f)
		# symlink to active theme static directory
		img_src = ''.join([current_app.config['UPLOADED_IMAGES_DEST'], filename])
		link = ''.join([current_app.config['STATIC_FOLDER'], filename])
		os.symlink(img_src, link)	
                src = url_for('static', filename=filename)
                jamla['items'][index]['primary_icon'] = {'src': src, 'type': ''}
            fp = open(current_app.config['JAMLA_PATH'], 'w')
            yaml.safe_dump(jamla,fp , default_flow_style=False)
        flash('Item(s) updated.')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_jamla.html', jamla=jamla, form=form)
#    return render_template('formarraybasic/index.html')

@admin_theme.route('/add', methods=['GET', 'POST'])                                      
@login_required                                                                  
def add_jamla_item():
    form = ItemsForm()
    jamla = get_jamla()
    if form.validate_on_submit():
        draftItem = {}
        draftItem['requirements'] = {}
        draftItem['primary_icon'] = {'src': '', 'type': ''}
        draftItem['title'] = form.title.data[0].strip()
        draftItem['requirements']['subscription'] = bool(form.subscription.data[0])
        if form.monthly_price.data[0] is None:
            draftItem['monthly_price'] = False
        else:
            draftItem['monthly_price'] = float(form.monthly_price.data[0]) * 100
        draftItem['requirements']['instant_payment'] = bool(form.instant_payment.data[0])
        if form.sell_price.data[0] is None:
            draftItem['sell_price'] = False
        else:
            draftItem['sell_price'] = float(form.sell_price.data[0]) * 100
        draftItem['selling_points'] = form.selling_points.data[0]
        # Create SKU
        draftItem['sku'] = form.title.data[0].replace(' ','')
        # Primary icon image storage
        f = form.image.data[0]
        if f:
            images = UploadSet('images', IMAGES)
            filename = images.save(f)
	    # symlink to active theme static directory
	    img_src = ''.join([current_app.config['UPLOADED_IMAGES_DEST'], filename])
	    link = ''.join([current_app.config['STATIC_FOLDER'], filename])
	    os.symlink(img_src, link)	
            src = url_for('static', filename=filename)
            draftItem['primary_icon'] = {'src': src, 'type': ''}
        jamla['items'].append(draftItem)
        fp = open(current_app.config['JAMLA_PATH'], 'w')
        yaml.safe_dump(jamla,fp , default_flow_style=False)
        flash('Item added.')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/add_jamla_item.html', jamla=jamla, form=form)

@admin_theme.route('/delete', methods=['GET'])
@login_required
def delete_jamla_item():
    jamla = get_jamla()
    return render_template('admin/delete_jamla_item_choose.html', jamla=jamla)

@admin_theme.route('/delete/<sku>', methods=['GET', 'POST'])
@login_required
def delete_item_by_sku(sku):
    jamla = get_jamla()
    jamlaApp = Jamla()
    jamlaApp.load(jamla=get_jamla())
    itemIndex = jamlaApp.sku_get_index(sku)
    if 'confirm' in request.args:
        confirm = False
        return render_template('admin/delete_jamla_item_choose.html', 
                                jamla=jamla, itemSKU=sku, confirm=False)
    if itemIndex is not False:
        # Perform removal
        jamla['items'].pop(itemIndex)
        fp = open(current_app.config['JAMLA_PATH'], 'w')                         
        yaml.safe_dump(jamla,fp , default_flow_style=False)

    flash("Item deleted.")
    return render_template('admin/delete_jamla_item_choose.html', jamla=jamla)

@admin_theme.route('/connect/gocardless/manually', methods=['GET', 'POST'])               
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
        return redirect(url_for('admin.dashboard'))                              
    else:                                                                        
        return render_template('admin/connect_gocardless_manually.html', form=form,    
                jamla=jamla, gocardless_connected=gocardless_connected)

@admin_theme.route('/connect/gocardless', methods=['GET'])                                
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

@admin_theme.route('/connect/gocardless/oauth/complete', methods=['GET'])                 
@login_required                                                                  
def gocardless_oauth_complete():                                                 
    jamla = get_jamla()                                                          
    jamlaApp = Jamla()                                                           
    jamlaApp.load(jamla=jamla)                                                   
    flow = OAuth2WebServerFlow(                                                  
            client_id=current_app.config['GOCARDLESS_CLIENT_ID'],                
            client_secret=current_app.config['GOCARDLESS_CLIENT_SECRET'],        
            scope="read_write",                                                  
            # You'll need to use exactly the same redirect URI as in the last
            # step
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
                                                                                 
    return redirect(url_for('admin.dashboard'))

@admin_theme.route('/connect/stripe/manually', methods=['GET', 'POST'])                   
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
        return redirect(url_for('admin.dashboard'))                              
    else:                                                                        
        return render_template('admin/connect_stripe_manually.html', form=form,        
                jamla=jamla, stripe_connected=stripe_connected)

@admin_theme.route('/connect/google_tag_manager/manually', methods=['GET', 'POST'])       
@login_required                                                                  
def connect_google_tag_manager_manually():                                       
    form = GoogleTagManagerConnectForm()                                         
    jamla = get_jamla()                                                          
    jamlaApp = Jamla()                                                           
    jamlaApp.load(jamla=jamla)                                                   
    if form.validate_on_submit():                                                
        container_id = form.data['container_id']                                 
        jamla['integrations']['google_tag_manager']['container_id'] = container_id
        jamla['integrations']['google_tag_manager']['active'] = True             
        # Overwrite jamla file with google tag manager container_id              
        fp = open(current_app.config['JAMLA_PATH'], 'w')                         
        yaml.safe_dump(jamla,fp , default_flow_style=False)                      
        session['google_tag_manager_container_id'] = container_id                
        return redirect(url_for('admin.dashboard'))                              
    else:                                                                        
        return render_template('connect_google_tag_manager_manually.html',       
                               form=form, jamla=jamla)

@admin_theme.route('/connect/tawk/manually', methods=['GET', 'POST'])                     
@login_required                                                                  
def connect_tawk_manually():                                                     
    form = TawkConnectForm()                                                     
    jamla = get_jamla()                                                          
    jamlaApp = Jamla()                                                           
    jamlaApp.load(jamla=jamla)                                                   
    if form.validate_on_submit():                                                
        property_id = form.data['property_id']                                   
        jamla['integrations']['tawk']['property_id'] = property_id               
        jamla['integrations']['tawk']['active'] = True                           
        # Overwrite jamla file with google tag manager container_id              
        fp = open(current_app.config['JAMLA_PATH'], 'w')                         
        yaml.safe_dump(jamla,fp , default_flow_style=False)                      
        session['tawk_property_id'] = property_id                                
        return redirect(url_for('admin.dashboard'))                              
    else:                                                                        
        return render_template('admin/connect_tawk_manually.html',                     
                               form=form, jamla=jamla)

@admin_theme.route('/jamla', methods=['GET'])                                             
@admin_theme.route('/api/jamla', methods=['GET'])                                         
@login_required                                                                  
def fetch_jamla():                                                               
    jamla = get_jamla()                                                          
    jamlaApp = Jamla()                                                           
    jamlaApp.load(jamla=jamla)                                                   
    #Strip out private values TODO don't store them here, move to .env?          
    jamla['payment_providers'] = None                                            
    resp = dict(items=jamla['items'], company=jamla['company'], name="fred",
email='me@example.com')
    return jsonify(resp)

@admin_theme.route('/push-payments', methods=['GET'])                                     
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
                'field_gocardless_subscription_id':
payment['links']['subscription'],
                'field_gocardless_amount_refunded': payment['amount_refunded'],  
                'field_gocardless_charge_date': payment['charge_date'],          
                'field_gocardless_created_at' : payment['created_at'],           
                'field_gocardless_creditor_id': payment['links']['creditor']     
            }                                                                    
            Rest.post(entity='transaction', fields=fields)                       
                                                                                 
    return "Payments have been pushed"

@admin_theme.route('/retry-payment/<payment_id>', methods=['GET'])                        
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

@admin_theme.route('/customers', methods=['GET'])
def customers():
    jamla = get_jamla()
    from SSOT import SSOT
    access_token = jamla['payment_providers']['gocardless']['access_token']
    target_gateways = ({'name': 'GoCardless', 'construct': access_token},)
    try:
        SSOT = SSOT(target_gateways)
        partners = SSOT.partners
    except gocardless_pro.errors.InvalidApiUsageError as e:
        print e.type
        print e.message
        flash("Invalid GoCardless API token. Correct your GoCardless API key.")
        return redirect(url_for('admin.connect_gocardless_manually'))
    except ValueError as e:
        print e.message
        if e.message == "No access_token provided":
            flash("You must connect your GoCardless account first.")
            return redirect(url_for('admin.connect_gocardless_manually'))
        else:
            raise
    return render_template('admin/customers.html', jamla=jamla,partners=partners)

@admin_theme.route('/transactions', methods=['GET'])
def transactions():
    jamla = get_jamla()
    from SSOT import SSOT
    access_token = jamla['payment_providers']['gocardless']['access_token']
    target_gateways = ({'name': 'GoCardless', 'construct': access_token},)
    try:
        SSOT = SSOT(target_gateways)
        transactions = SSOT.transactions
    except gocardless_pro.errors.InvalidApiUsageError as e:
        print e.type
        print e.message
        flash("Invalid GoCardless API token. Correct your GoCardless API key.")
        return redirect(url_for('admin.connect_gocardless_manually'))
    except ValueError as e:
        print e.message
        if e.message == "No access_token provided":
            flash("You must connect your GoCardless account first.")
            return redirect(url_for('admin.connect_gocardless_manually'))
        else:
            raise
    return render_template('admin/transactions.html', jamla=jamla,transactions=transactions)

def getItem(container, i, default=None):                                         
    try:                                                                         
        return container[i]                                                      
    except IndexError:                                                           
        return default 
