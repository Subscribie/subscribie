import Rest
from flask import g, request, redirect, url_for, session
from functools import wraps
import json

def create_partner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print "Creating partner of customer type.."
            title = request.form['given_name'] + request.form['family_name']
            fields = {
                'title':title,
                'field_customer': 1
            }
            r = Rest.post(entity='partner', fields=fields)
            resp = json.loads(r.text)
            partner_nid = resp['nid'][0]['value']
            print "Partner node id is: " + str(partner_nid)
            session['partner_nid'] = partner_nid
        except Exception as e:
            print "Failed creating partner of customer type.."
            print e
        return f(*args, **kwargs)
    return decorated_function

def create_contact(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print "Creating contact.."
            fname = request.form['given_name']
            lname = request.form['family_name'] 
            title = fname + lname
            mobile = request.form['mobile']
            email = request.form['email'] 
            address_line1 = request.form['address_line1']
            city = request.form['city']
            postcode = request.form['postal_code']
            fields = {
                'title':title,
                'field_first_name': fname,
                'field_last_name' : lname,
                'field_mobile': mobile,
                'field_email' : email,
                'field_address_line_1': address_line1,
                'field_city' : city,
                'field_postcode' : postcode
            }
            r = Rest.post(entity='contact', fields=fields)
            resp = json.loads(r.text)
            contact_nid = resp['nid'][0]['value']
            print "Contact node id is: " + str(contact_nid)
            session['contact_nid'] = contact_nid
        except Exception as e:
            print "Failed creating contact..."
            print e
        return f(*args, **kwargs)
    return decorated_function

def attach_contact_partner(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            print "Attaching contact to partner record.."
            #Get uuid of contact record
            contact = Rest.get("/api/contact/" + str(session['contact_nid']))
            contact_uuid = contact.json()[0]['uuid'][0]['value']
            print "The contact uuid is: " + contact_uuid
            embeded = {'field_contacts':[{'uuid':contact_uuid}]}
            r = Rest.patch(nid=session['partner_nid'], entity='partner', fields=None, embeded=embeded)
        except Exception as e:
            print "Failed attaching contact to partner record..."
            print e
        return f(*args, **kwargs)
    return decorated_function
