import os
from os import environ
from subprocess import Popen, PIPE
import datetime
import urlparse
import requests
import werkzeug
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
from werkzeug.exceptions import HTTPException, NotFound, default_exceptions
from werkzeug.wsgi import SharedDataMiddleware
from werkzeug.utils import redirect
from jinja2 import Environment, FileSystemLoader
from werkzeug.contrib.sessions import SessionMiddleware, \
          FilesystemSessionStore
from bs4 import BeautifulSoup
import gocardless_pro
import sqlite3
import smtplib

class Shortly(object):
    session_store = FilesystemSessionStore()

    def __init__(self, config):
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path),
                                     autoescape=True)
        self.gocclient = gocardless_pro.Client(
            access_token = os.getenv('gocardless_token'),
            environment= os.getenv('gocardless_environment')
        )
        self.url_map = Map([
            Rule('/', endpoint='start'),
            Rule('/broadband-availability-postcode-checker', endpoint='broadband_availability_postcode_checker'),
            Rule('/sign', endpoint='sign'),
            Rule('/new_customer', endpoint='new_customer'),
            Rule('/establish_mandate', endpoint='establish_mandate'),
            Rule('/complete_mandate', endpoint='complete_mandate'),
            Rule('/thankyou', endpoint='thankyou'),
            Rule('/gettingstarted', endpoint='gettingstarted'),
            Rule('/prerequisites', endpoint='prerequisites'),
            Rule('/manifest.json', endpoint='manifest'),
            Rule('/app.js', endpoint='appjs'),
            Rule('/sw.js', endpoint='sw')
        ])

    #####################
    #   Error Routes
    #####################

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

    def on_thankyou(self, request):
        return self.render_template('thankyou.html')

    def on_gettingstarted(self, request):
        return self.render_template('gettingstarted.html')

    def on_prerequisites(self, request):
        """
        Render template with mandatory questions for a
        sucessful onboarding e.g. "Do you already have
        a x,y,z?".
        """
        return self.render_template('prerequisites.html')

    def on_broadband_availability_postcode_checker(self,request):
        return self.render_template('broadband-availability-postcode-checker.html')

    def on_new_customer(self, request):
        if request.method == 'POST':
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
            sid = request.cookies.get('karma_cookie')
            con = sqlite3.connect(os.getenv("db_full_path"))
            cur = con.cursor()
            cur.execute("INSERT INTO person VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (sid, now, given_name, family_name, address_line1, city, postal_code, email, mobile, wants, 'null', 'null'))
            con.commit()
            cur.execute("SELECT * FROM person")
            print cur.fetchone()
            con.close()

            #TODO: redirect to Crab
            return redirect(os.getenv('establish_mandate_url'))

        #GET request
        else:
            package = request.args["plan"]
            return self.render_template('new_customer.html', package=package)

    def on_establish_mandate(self, request):
        #lookup the customer with sid and get their relevant details
        sid = request.cookies.get('karma_cookie')
        con = sqlite3.connect(os.getenv("db_full_path"))
        cur = con.cursor()
        cur.execute("SELECT * FROM person p WHERE p.sid = ?", (sid,))
        res = cur.fetchone()
        print res
        con.close()

        if res:
            #TODO: validate that hasInstantPaid is true for the customer

            redirect_flow = self.gocclient.redirect_flows.create(
                params = {
                    "description" : "Karma Computing Broadband",
                    "session_token" : sid,
                    "success_redirect_url" : os.getenv('success_redirect_url'),
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
            print "no customer found with sid"
            #TODO: respond with 400

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

        # Store customer
        sid = request.cookies.get('karma_cookie')
        now = datetime.datetime.now()
        mandate = redirect_flow.links.mandate
        customer = redirect_flow.links.customer
        flow = redirect_flow_id

        con = sqlite3.connect(os.getenv('db_full_path'))
        cur = con.cursor()
        cur.execute("INSERT INTO mandates VALUES (?, ?, ?, ?, ?)", (sid, now, mandate, customer, flow))
        con.commit()
        cur.execute("SELECT * FROM mandates")
        print cur.fetchone()
        con.close()


        # Display a confirmation page to the customer, telling them
        # their Direct Debit has been set up. You could build your own,
        # or use ours, which shows all the relevant information and is
        # translated into all the languages we support.
        print("Confirmation URL: {}".format(redirect_flow.confirmation_url))
        return redirect(os.getenv('thankyou_url'))

    def on_start(self,request):
        error = None
        nophone = False
        try:
            if 'nophone' in request.headers['Cookie']:
                nophone=True
        except  KeyError:
            pass
        result = ''
        if request.method == 'POST':
            print(os.getenv('db_full_path'))
            buildingnumber = request.form['buildingnumber']
            PostCode = request.form['PostCode']
            now = datetime.datetime.now()
            prettyTime = datetime.datetime.now().strftime("%H:%M %D")
            sid = request.cookies.get('karma_cookie')
            con = sqlite3.connect(os.getenv('db_full_path'))
            cur = con.cursor()
            cur.execute("INSERT INTO lookups VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (sid, now, buildingnumber, '', '', '', '', PostCode))
            con.commit()
            cur.execute("SELECT * FROM lookups")
            print cur.fetchone()
            con.close()
            canADSL = False
            canFibre = False
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
                try:
                    if 'nophone' in request.headers['Cookie']:
                        nophone=True
                except  KeyError:
                    pass
                uptoSpeedFibre = result['VDSL Range A']['Downstream']['high']
                uptoSpeedADSL = result['WBC ADSL 2+']['Downstream']
                return self.render_template('result.html', result=result, canADSL=canADSL, canFibre=canFibre, buildingnumber=buildingnumber, postCode=PostCode, now=prettyTime, nophone=nophone)
        return self.render_template('start.html', error=error, cheese=True, nophone=nophone)





    def insert_url(self, url):
        short_id = self.redis.get('reverse-url:' + url)
        if short_id is not None:
            return short_id
        url_num = self.redis.incr('last-url-id')
        short_id = base36_encode(url_num)
        self.redis.set('url-target:' + short_id, url)
        self.redis.set('reverse-url:' + url, short_id)
        return short_id

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
        try:
            self.session_store.save(request.session)
            response.set_cookie('karma_cookie', request.session.sid)
        except AttributeError as e:
            pass

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

def source(script, update=1):
    pipe = Popen(". %s; env" % script, stdout=PIPE, shell=True)
    data = pipe.communicate()[0]

    env = dict((line.split("=", 1) for line in data.splitlines()))
    if update:
        environ.update(env)

    return env

if __name__ == '__main__':
    source("./.env")
    from werkzeug.serving import run_simple
    app = create_app()
    if (os.getenv('environment') == 'local'):
        run_simple('0.0.0.0', 5000, app, use_debugger=False, use_reloader=True, ssl_context='adhoc')
    else:
        run_simple('0.0.0.0', 5000, app, use_debugger=False, use_reloader=True)

#source(r"/Users/connorloughlin/KC - Development/broadband-availability-checker/shortly/.env")
source('.env')

application = create_app()
