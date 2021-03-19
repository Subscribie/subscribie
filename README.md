[![Gitter](https://badges.gitter.im/Subscribie/community.svg)](https://gitter.im/Subscribie/community)

# Subscribie  - Subscription Website Builder 
#### variable subscription & recurring payments

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
- Stripe for subscriptions & one-off payments

An abstraction layer for managing variable recurring subscriptions and billing. Abstracts direct debit and token based card payment providers or payment-institutions.

Keywords: subscriptions, payments, PS2, SEPA

Want to be involved? See [CONTRIBUTING.md](CONTRIBUTING.md) and quickstart below.

# Quickstart (without Docker)

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
cp .env.example .env # Copy default .env settings (read it)
virtualenv -p python3 venv # Create a python3.x virtualenv
. venv/bin/activate # Activate the virtualenv
pip install -r requirements.txt # Install requirements
export FLASK_APP=subscribie
export FLASK_DEBUG=1
flask db upgrade
# The database file will be called "data.db". It will be *above* your current directory
flask initdb # This wil insert pretend data into your database.
flask run # Run the app
```
Now visit http://127.0.0.1:5000

# Quickstart (with Docker compose)

If you like to use docker-compose workflow for local development:

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
cp .env.example .env
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1
# Build is only required if you want to force the image to be rebuilt
# --force-recreate is for recreating the container (not the image)
docker-compose up --build --force-recreate
```

Then visit http://127.0.0.1:5000

To go inside the container, you can do: `docker-compose exec web /bin/bash` 
from the project root directory.

To rebuild the latest container, stop docker compose then do: `docker-compose build`.

# How to change theme (theme development)

### How to change from the default jesmond theme to the builder theme.

1. Edit your `.env` file

Change:

- `THEME_NAME="jesmond"` to `THEME_NAME="builder"`
- **(optional)** change `TEMPLATE_BASE_DIR` if you want to store themes in a different directory.

2. Stop & start subscribie

3. Complete. The other theme will now load

#### Create a new theme

If you're creating a *new* theme, then change `TEMPLATE_BASE_DIR` to a directory **outside** of 
subscribie root project.


# API based authentication with jwt token

Provide the username & password in a POST request, and a jwt token is returned for 
use in further requests. 

# Testing Stripe webhooks locally

1. Install stripe cli https://stripe.com/docs/stripe-cli#install
2. Login into stripe via `stripe login` (this shoud open the browser with stripe page where you should enter your credentials). If this command doesn't work use `stripe login -i` (this will login you in interactive mode where instead of opening browser you'll have to put stripe secret key directly into terminal)
3. Run `stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5000/stripe_webhook`
4. Copy the webhook secret from the output "Ready! Your webhook signing secret is **whsec_abc123..**" into your `STRIPE_WEBHOOK_ENDPOINT_SECRET` inside `.env` file

```
stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5000/stripe_webhook
```

This will allow you to see/process webhook requests locally using test api keys. Note that in production, stripe webhooks are proxied via https://github.com/Subscribie/stripe-connect-webhook-endpoint-router which validates every webhook before it get forwarded.

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
python -m pytest --ignore=node_modules # run pytest
```

## Automated browser testing with playright

Run npm install & pray to the npm gods.
```
npm install
```

Might see `UnhandledPromiseRejectionWarning: browserType.launch: Host system is missing dependencies!`
```
  Install missing packages with:
      sudo apt-get install libgstreamer-plugins-bad1.0-0\
          libenchant1c2a
```

The https://github.com/Subscribie/stripe-connect-account-announcer
needs to be running locally if you're runnning browser automated tests
locally.

Then, to run playwright tests:

```
npm test
```

# Saas Deployment

Needed components / services. Check the `.env.example` for each of them.

- A [redis instance](https://github.com/Subscribie/redis), listening on localhost only (unless [protected with iptables](https://github.com/Subscribie/redis#ip-tables-config-example))
- A subscribie site with the [Builder module](https://github.com/Subscribie/module-builder) installed. The builder module submits new sites for building
- [Subscribie deployer](https://github.com/Subscribie/subscribie-deployer) is an endpoint which listens for `POST` requests of new sites to be created. The [Builder module](https://github.com/Subscribie/module-builder) submits to this endpoint. The server requires [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/Install.html) to be installed. There is an example config in the [README](https://github.com/Subscribie/subscribie-deployer).
- [Stripe connect account announcer](https://github.com/Subscribie/stripe-connect-account-announcer) Each shop announces its [stripe connect account id](https://stripe.com/docs/api/connected_accounts) to a redis endpoing (key is the account id, value is the shop url)
- [Stripe webhook router](https://github.com/Subscribie/stripe-connect-webhook-endpoint-router) which routes webhooks to the correct shop

#### Checklist 

- [ ] A Redis hostname is set
- [ ] Redis is configured with password authentication
- [ ] Iptables are configured for redis
- [ ] Hostname is setup for stripe-connect-webhook-endpoint-router
- [ ] Hostname is setup for stripe-connect-account-announcer (listening on port 8001 by default)

# Where can I get more help, if I need it?

Read through the [docs](https://subscribie.readthedocs.io)
Submit a detailed [issue](https://github.com/Subscribie/subscribie/issues)

