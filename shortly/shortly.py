import os
import urlparse
import requests
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader
from werkzeug.contrib.sessions import SessionMiddleware, \
          FilesystemSessionStore
from bs4 import BeautifulSoup
import gocardless_pro
import sqlite3

class Shortly(object):
    session_store = FilesystemSessionStore()

    def __init__(self, config):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.gocclient = gocardless_pro.Client(
            access_token ='sandbox_Cgp7gAVXCNsc_vStksIq2bqfNgT7TFXd2zarJZHe',
            environment='sandbox'
        )
        self.url_map = Map([
            Rule('/', endpoint='new_url'),
            Rule('/sign', endpoint='sign'),
            Rule('/new_customer', endpoint='new_customer'),
            Rule('/complete_mandate', endpoint='complete_mandate'),
            Rule('/pay', endpoint='pay'),
            Rule('/manifest.json', endpoint='manifest'),
            Rule('/app.js', endpoint='appjs'),
            Rule('/sw.js', endpoint='sw'),
        ])

    def on_appjs(self, template_name, **context):
        return Response(file('app.js'), direct_passthrough=True, mimetype='application/javascript')


    def on_manifest(self, template_name, **context):
        return Response(file('manifest.json'), direct_passthrough=True, mimetype='application/json')

    def on_sw(self, template_name, **context):
        return Response(file('sw.js'), direct_passthrough=True, mimetype='application/javascript')

    def render_template(self, template_name, **context):
        t = self.jinja_env.get_template(template_name)
        return Response(t.render(context), mimetype='text/html')

    def on_sign(self,request):
        return self.render_template('signature.html')

    def on_pay(self, request):
        customers = self.gocclient.customers.list().records
        print(customers)
        print([customer.email for customer in customers])
        if request.method == 'POST':
            return self.render_template('thankyou.html', customers=customers)
        return self.render_template('pay.html', customers=customers)

    def on_new_customer(self, request):
        if request.method == 'POST':
            given_name = request.form['given_name']
            family_name = request.form['family_name']
            address_line1 = request.form['address_line1']
            city = request.form['city']
            postal_code = request.form['postal_code']
            email = request.form['email']

            redirect_flow = self.gocclient.redirect_flows.create(
                params = {
                    "description" : "Karma Computing Broadband",
                    "session_token" : request.cookies.get('karma_cookie'),
                    "success_redirect_url" : "http://localhost:5000/complete_mandate",
                    "prefilled_customer" : {
                        "given_name" : given_name,
                        "family_name": family_name,
                        "address_line1": address_line1,
                        "city" : city,
                        "postal_code": postal_code,
                        "email": email,
                    }
                }
            )
            # Hold on to this ID - we'll need it when we 
            # "confirm" the dedirect flow later
            print("ID: {} ".format(redirect_flow.id))
            print("URL: {} ".format(redirect_flow.redirect_url))
            return redirect(redirect_flow.redirect_url)
        else:
            return self.render_template('new_customer.html')
        
    def on_complete_mandate(self, request):
        redirect_flow_id = request.args.get('redirect_flow_id')
        print("Recieved flow ID: {} ".format(redirect_flow_id))

        redirect_flow = self.gocclient.redirect_flows.complete(
            redirect_flow_id,
            params = {
                "session_token": request.cookies.get('karma_cookie')
        })
        print ("Mandate: {}".format(redirect_flow.links.mandate))
        # Save this mandate ID for the next section.
        print ("Customer: {}".format(redirect_flow.links.customer))

        # Display a confirmation page to the customer, telling them 
        # their Direct Debit has been set up. You could build your own, 
        # or use ours, which shows all the relevant information and is 
        # translated into all the languages we support.
        print("Confirmation URL: {}".format(redirect_flow.confirmation_url))
        return redirect(redirect_flow.confirmation_url)


    def on_new_url(self,request):
        error = None
        result = ''
        if request.method == 'POST':
            buildingnumber = request.form['buildingnumber']
            PostCode = request.form['PostCode']
            sid = request.cookies.get('karma_cookie')
            con = sqlite3.connect('karma.db')
            cur = con.cursor()
            cur.execute("INSERT INTO lookups VALUES (?, ?, ?)", (buildingnumber, PostCode, sid))
            con.commit()
            cur.execute("SELECT * FROM lookups")
            print cur.fetchone()
            canADSL = False
            canFibre = False
            if not is_valid_lookup(request.form):
                error = 'Please enter a valid request'
            else:
                r = requests.post('https://www.dslchecker.bt.com/adsl/ADSLChecker.AddressOutput', 
                                 data = {'buildingnumber': request.form['buildingnumber'],
                                       'PostCode': request.form['PostCode']})
                result = r.text
                soup = BeautifulSoup(r.text, 'html.parser')
                soup.prettify()
                soup.find_all('span')
                result = {}
                result['VDSL Range A'] = {'Downstream': {'high':'', 'low':''},'Upstream': {'high':'', 'low':''}}
                result['WBC ADSL 2+'] = {'Downstream': '','Upstream': ''}

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
                return self.render_template('result.html', result=result, canADSL=canADSL, canFibre=canFibre)
        return self.render_template('new_url.html', error=error, cheese=True)



    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except HTTPException, e:
            return e


    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        sid = request.cookies.get('karma_cookie')
        if sid is None:
            request.session = self.session_store.new()
        else:
            request.session = self.session_store.get(sid)
        self.session_store.save(request.session)
        response.set_cookie('karma_cookie', request.session.sid)

        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)

def create_app(redis_host='localhost', redis_port=6379, with_static=True):
    app = Shortly({
        'redis_host': redis_host,
        'redis_port': redis_port
    })
    if with_static:
        app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
            '/static': os.path.join(os.path.dirname(__file__), 'static')
        })
    return app

def is_valid_lookup(form):
    return True

def base36_encode(number):
    assert number >= 0, 'positive integer required'
    if number == 0:
        return '0'
    base36 = []
    while number != 0:
        number, i = divmod(number, 36)
        base36.append('0123456789abcdefghijklmnopqrstuvwxyz'[i])
    return ''.join(reversed(base36))

if __name__ == '__main__':
    from werkzeug.serving import run_simple
    app = create_app()
    run_simple('127.0.0.1', 5000, app, use_debugger=True, use_reloader=True)

application = create_app()


