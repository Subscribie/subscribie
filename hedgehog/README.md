# Setup 

### Create database
python createdb.py

### Create .env file
Example .env file:
export establish_mandate_url=http://localhost:5000/establish_mandate 
export success_redirect_url=http://localhost:5000/complete_mandate
export thankyou_url=http://localhost:5000/thankyou
export db_full_path=./kcBroadband.db
export gocardless_token="GET_FROM_GOCARDLESS"
export gocardless_environment="use sandbox (testing) or live"

### Run the script locally

`sudo python shortly.py`

Note: On the server, the app is presented as a wsgi application which apache loads in
see: http://modwsgi.readthedocs.io/en/develop/user-guides/quick-configuration-guide.html 
(looks more complicated that it is)

## Protecting routes

Decorate a protected route with a `@flask_login.login_required` decorator after
your `@app.route('/path')` decorators.

We use the flask_login for authenticated session management, so all docs there will be relevant: https://github.com/maxcountryman/flask-login

E.g: To mage a route 'protected'

        @app.route('/my-account-page')                                                 
        @flask_login.login_required                                              
        def myaccount():                                                         
            return 'My account page'
