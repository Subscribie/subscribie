# Subscribie  - Subscription Website Builder 
#### variable subscription & recurring payments
[![Build Status](https://travis-ci.org/Subscribie/subscribie.svg?branch=master)](https://travis-ci.org/Subscribie/subscribie)

### What does this project do?                                                   

Quickly build a subscription based website, taking variable monthly payments.

- You have a subscription service to sell
- Each of your packages have unique selling points (USPs)
- Each have a different reoccurring price

Use Subscribie to build your subscription model business & test your market.

# Why is this project useful?                                                    

A lot of the hard work has been done for you. If you're a devloper, you can
impress your clients quickly, if you're a small business owner, you might want
to try the [subscription website hosting service](http://subscriptionwebsitebuilder.co.uk) but you can always host it yourself too.

- Low risk (not very expensive)
- No coding required
- Simple: Just give us your USPs for each service & price
- Upload your pictures
- Choose between Stripe & Gocardless (more coming soon!) 

An abstraction layer for managing variable recurring subscriptions and billing. Abstracts direct debit and token based card payment providers or payment-institutions.

Keywords: subscriptions, payments, PS2, SEPA 

# Quickstart

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
cp .env.example .env # Copy default .env settings (look at it)
virtualenv -p python3 venv # Create a python3.x virtualenv
. venv/bin/activate # Activate the virtualenv
pip install -r requirements.txt # Install requirements
export FLASK_APP=subscribie
export FLASK_DEBUG=1
flask run # Run the app
```
Now visit http://127.0.0.1:5000


# Docs 

https://subscribie.readthedocs.io

# API based authentication with jwt token

Provide the username & password in a POST request, and a jwt token is returned for 
use in further requests. 

Oauth style login:

```
curl -v -d "username=me@example.com" -d "password=password" http://127.0.0.1:5000/auth/jwt-login
```
Http Basic auth login:

```
curl -v --user "fred:password" http://127.0.0.1:5000/auth/jwt-login
```

Then use the bearer token in a request to a protect path.
e.g.
```
curl -v -H "Authorization: Bearer <token>" http://127.0.0.1:5000/auth/protected
```
# Demo

https://subscriptionwebsitebuilder.co.uk

# Tests

To run tests:

```
. venv/bin/activate # activate virtualenv
python -m pytest # run pytest
```

# Where can I get more help, if I need it?

Read through the [docs](https://subscribie.readthedocs.io)
Submit a detailed [issue](https://github.com/Subscribie/subscribie/issues)

