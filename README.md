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

# Quickstart (without Docker)

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

# Quickstart (with Docker compose)

If you like to use docker-compose workflow for local development:

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
cp .env.docker.example .env
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
docker-compose up
```

Then visit http://127.0.0.1:5000

If you see `File doesn't exist` in the output, the you have probably forgotten
to `cp .env.docker.example .env` to the project root directory.

To go inside the container, you can do: `docker-compose exec web /bin/bash` 
from the project root directory.

To rebuild the latest container, stop docker compose then do: `docker-compose build`.

# How to change theme (theme development)

### How to change from the default jesmond theme to the builder theme.

1. Edit your `.env` file

Change:

- `THEME_NAME="jesmond"` to `THEME_NAME="builder"`
- `STATIC_FOLDER="./subscribie/themes/theme-jesmond/static/"` to `STATIC_FOLDER="./subscribie/themes/theme-builder/static/"`
- **(optional)** change `TEMPLATE_BASE_DIR` if you want to store themes in a different directory.

2. Stop & start subscribie

3. Complete. The other theme will now load

#### Create a new theme

If you're creating a *new* theme, then change `TEMPLATE_BASE_DIR` to a directory **outside** of 
subscribie root project.

# Docs 

https://subscribie.readthedocs.io

# API based authentication with jwt token

Provide the username & password in a POST request, and a jwt token is returned for 
use in further requests. 

# Testing Stripe webhooks locally

1. Install stripe cli https://stripe.com/docs/stripe-cli#install
2. Run stripe cli
3. Copy the webhook secret "Ready! Your webhook signing secret is whsec_abc123.."
3. In your `.env` file set `STRIPE_WEBHOOK_ENDPOINT_SECRET` to the webhook secret

```
stripe listen --forward-to 127.0.0.1:5000/stripe_webhook
```

This will allow you to see/process webhook requests locally using test api keys.

# API Basics

## Oauth style login:

```
curl -v -d "username=me@example.com" -d "password=password" http://127.0.0.1:5000/auth/jwt-login
```
## Http Basic auth login:

```
curl -v --user "fred:password" http://127.0.0.1:5000/auth/jwt-login
```

Then use the bearer token in a request to a protect path.
e.g.
```
curl -v -H "Authorization: Bearer <token>" http://127.0.0.1:5000/auth/protected
```

## Create Plan 

Example POST request:
```
    curl -v -H "Content-Type: application/json" 
    -H "Authorization: Bearer <token>" -d '
    {
      "interval_unit": "monthly",
      "interval_amount": "599",
      "sell_price": 0,
      "title": "My title",
      "requirements": {
        "instant_payment": false,
        "subscription": true,
        "note_to_seller_required": false
      },
      "selling_points": [
        {"point":"Quality"}
      ]
    }' http://127.0.0.1:5000/api/plan
```

## Update Plan

Example PUT request:
```
    curl -v -H 'Content-Type: application/json' -X PUT 
    -d '
    {
      "title":"Coffee", 
      "interval_unit": "monthly", 
      "selling_points": [
        {"point":"Quality"}, 
        {"point": "Unique blend"}
      ], 
      "interval_amount":888, 
      "requirements": {
        "instant_payment": false, 
        "subscription": true, 
        "note_to_seller_required": false}
    }' 
    http://127.0.0.1:5000/api/plan/229
```

## Delete Plan

Example DELETE request:
```
curl -v -X DELETE -H "Authorization: Bearer <token>" http://127.0.0.1:5000/api/plan/229
```

# Demo

https://subscriptionwebsitebuilder.co.uk

# Tests

To run tests:

```
. venv/bin/activate # activate virtualenv
python -m pytest # run pytest

## Autmated browser testing with playright


```
npm i -D playwright
```

Might see `UnhandledPromiseRejectionWarning: browserType.launch: Host system is missing dependencies!`
```
  Install missing packages with:
      sudo apt-get install libgstreamer-plugins-bad1.0-0\
          libenchant1c2a
```

```

# Where can I get more help, if I need it?

Read through the [docs](https://subscribie.readthedocs.io)
Submit a detailed [issue](https://github.com/Subscribie/subscribie/issues)

