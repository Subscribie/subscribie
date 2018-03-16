from penguin_rest import Rest
from flask import g, request, redirect, url_for
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
            print r
        except Exception as e:
            print "Failed creating partner of customer type.."
            print e
        return f(*args, **kwargs)
    return decorated_function
