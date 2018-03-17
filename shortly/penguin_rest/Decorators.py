from penguin_rest import Rest
from flask import g, request, redirect, url_for, session
from functools import wraps
import json

def create_customer(f):
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
            #Test updating (patch) a partner
            fields = { 
                'field_customer':0,
                'title':"changed"
            }
            # Test updated embeded field referenced (patch) a partner with 
            # multiple contacts
            embeded = {'field_contacts':[{'uuid':'8d19ade2-8486-4522-b8a1-920b308c8318'}, {'uuid':'c685897a-8435-40f0-b2e2-35b26051bff8'}]}

            Rest.patch(nid=partner_nid, entity='partner', fields=fields, embeded=embeded)

        except Exception as e:
            print "Failed creating partner of customer type.."
            print e
        return f(*args, **kwargs)
    return decorated_function
