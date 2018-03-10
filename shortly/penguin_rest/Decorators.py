from penguin_rest import Rest
from flask import g, request, redirect, url_for
from functools import wraps

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
            Rest.post(entity='partner', fields=fields)
        except:
            print "Failed creating partner of customer type.."
            pass
        return f(*args, **kwargs)
    return decorated_function
