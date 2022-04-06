[![Gitter](https://badges.gitter.im/Subscribie/community.svg)](https://gitter.im/Subscribie/community)

# Subscribie  - Collect recurring payments easily 

- [Features](#features)
- [Demo & Hosting](#demo--hosting)
- [Quickstart](#quickstart-without-docker)
- [Testing](#testing)
- [SaaS Deployment](#saas-deployment)
  - [Architecture Overview](#architecture)
  - [Application server](#application-server-uwsgi)
#### Open Source subscription billing and management


## Demo
https://footballclub.subscriby.shop/
<a href="https://footballclub.subscriby.shop/" target="_blank">
<img src="https://user-images.githubusercontent.com/1718624/157171840-6d19fdea-397d-4686-b812-a80f0e15f81e.png" /></a>


## What does this project do?
Use Subscribie to collect recurring payments online.

Quickly build a subscription based website, taking weekly/monthly/yearly payments- including one-off charges.

- You have subscription service(s) to sell (plans)
- Each of your plans have unique selling points (USPs)
- Each have a different recurring price, and/or an up-front charge

# Demo & Hosting
Don't want/know how to code? Pay for the hosted service.

https://subscribie.co.uk

# Developer Quickstart
Quickly run Subscribie from a container:

If you use `podman`:
```
podman run -p 8082:80 ghcr.io/subscribie/subscribie/subscribie:latest
```

Or, if you prefer Docker:
```
docker run -p 8082:80 ghcr.io/subscribie/subscribie/subscribie:latest
```
Then visit: http://127.0.0.1:8082/auth/login

Username: admin@example.com

Password: password

[More about containers](https://mkdev.me/en/posts/the-tool-that-really-runs-your-containers-deep-dive-into-runc-and-oci-specifications).

# Features
Quickly set-up a subscription site which can:

- Collect recurring payments weekly / monthly / yearly ✔️ 
- Sell subscription plans with an up-front cost ✔️
- Sell subscription plans with both a recurring & an upfront cost ✔️
- Create free trial plans which automatically charge after trial expires ✔️
- Pause subscriptions ✔️
- Cancel active subscriptions ✔️
- Refund individual transactions ✔️
- Charge customers ad-hoc outside of their subscription (e.g. chrage for ad-hoc additonal support) ✔️ 
- Create private plans which are hidden from the main shop ✔️
- Create subscription payment links which I can send to people to sign up to ✔️
- Recieve payments to my bank account daily from my subscribers ✔️
- Automatically generate invoices for every payment ✔️
- Automatically charge VAT to plans if VAT registered ✔️
- Show the VAT amount on invoices if VAT registerd ✔️
- Embed my shop in an existing website ✔️
- Upload simple files (images, documents) to my shop, which only paying subscribers can see ✔️
- View a history of all transactions which have happend through my shop ✔️
- View all payment history of individual subscribers ✔️
- Search payments by subscriber name ✔️
- Search payments by plan name ✔️
- Search payments by plan name & subscriber name ✔️
- Add additonal team members to my shop to manage it ✔️
- My Subscribers can login to their account and change their payment details ✔️
- My Subscribers can login to their account and view their plans ✔️
- My Subscribers can login to their account and download the files I have uploaded to my shop ✔️
- My Subscribers can login to their account and vew the private pages I've created once they're logged in ✔️
- Delay the number of days before the first payment (useful for cooling off period) ✔️
- Set a cancel at date on plans so that payments automatically stop on a specified date ✔️
- View statistics on the number of active subscribers ✔️
- [Divide my plans into categories](https://subscriptionwebsitebuilder.co.uk/blog/how-to-use-categories-in-subscribie/) ✔️
- Require a simple text note from the customer during sign-up ✔️
- Present 'options' and 'choices' to customers during signup, for example colour 'red, green or blue'? ✔️
- Create subscription plans with a description & unique selling points ✔️
- View upcomming payments ✔️
- Export my subscribers as a csv ✔️
- Export all transactions as a csv ✔️
- Arrange the order that plans appear on my shop ✔️
- Upload an image on each of my plans ✔️
- Create basic pages on my shop, such as an about page ✔️
- Create private pages which only my subscribers can see ✔️
- Customise the welcome email to my subscribers ✔️
- Change the 'reply-to' email on the welcome email to my subscribers ✔️
- Upload my company logo ✔️
- Set the slogan of my business ✔️
- Integrate online chat with your shop ✔️
- Inject custom code snippets ✔️
- Integrate with google analytics ✔️
- Change the colour of my shop ✔️
- Is mobile friendly ✔️

# Why is this project useful?                                                    

A lot of the hard work has been done for you. If you're a devloper, you can
impress your clients quickly, if you're a small business owner, you might want
to try the [subscription website hosting service](http://subscriptionwebsitebuilder.co.uk) but you can always host it yourself too.

- Low risk (not very expensive)
- No coding required
- Simple: Just enter your plans & prices
- Upload a picture
- Uses Stripe for subscriptions & one-off payments

# Contributing & Help finding things: Where do I find x? Where is file y?

See [CONTRIBUTING.md](CONTRIBUTING.md) and quickstart below.

# Quickstart (without Docker)

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
cp .env.example .env # Copy default .env settings (read it)
# Read the .env file so you're familiar with the env variables
```

(Optional) Set database path. Edit `.env` and set `DB_FULL_PATH` and `SQLALCHEMY_DATABASE_URI`. (optional but recommended- do not store data.db in /tmp).

> Notice that `sqlite:///` starts with *three* forward slashes. So, if you want to store the database in `/home/sam/data.db` then,
you should put `sqlite:////home/sam/data.db` (note four `/`'s)

```
# Open the .env file, and change the database path to store somewhere else (e.g. your `/home/Documents/data.db` folder):

DB_FULL_PATH="/tmp/data.db"
SQLALCHEMY_DATABASE_URI="sqlite:////tmp/data.db"
```

Create python environment and run flask:
```
python3 -m venv venv # Create a python3.x virtual environment
. venv/bin/activate # Activate the virtualenv
pip install -r requirements.txt # Install requirements
export FLASK_APP=subscribie
export FLASK_DEBUG=1
flask db upgrade
flask initdb # (recommended- gives you some example data)
```

The database file is called `data.db`. Note,
`flask initdb` inserts pretend data into your database for testing.

### Set Stripe API key
You need a Stripe api key.

1. Create a stripe account
2. Go to api keys https://dashboard.stripe.com/test/apikeys (test mode)
3. Copy `Publishable key` and `Secret key`
4. Paste the keys into your `.env` file:

Edit your .env file
```
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_<your-Publishable-key>
STRIPE_TEST_SECRET_KEY=sk_test_<your-Secret-key>
```

## Start Subscribie
```
export FLASK_APP=subscribie
export FLASK_DEBUG=1
flask run
```
Now visit http://127.0.0.1:5000

# Quickstart (with Docker)

If you like to use docker-compose workflow for local development:

```
git clone https://github.com/Subscribie/subscribie.git
cd subscribie
cp .env.example .env
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_BUILDKIT=1

# Start the container
docker-compose up

# Wait for it to build...
```

Then visit http://127.0.0.1:5000

To go inside the container, you can do: `docker-compose exec web /bin/bash` 
from the project root directory.

# Testing

### How to setup/run tests

There are two types of test
- Browser automated tests using [playwright](https://github.com/microsoft/playwright)
- Basic Python tests

### Run Basic Python Tests:

```
. venv/bin/activate # activates venv
python -m pytest --ignore=node_modules # run pytest
```

#### Receive Stripe webhooks locally whilst testing

Stripe webhooks are recieved when payment events occur.
The test suite needs to listen to these events locally when running tests.

tldr: 
1. Install the stripe cli
2. Run `stripe listen --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed --forward-to 127.0.0.1:5000/stripe_webhook`

## Concept: What are [Stipe Webhooks](https://stripe.com/docs/webhooks)?
> Stripe takes payments. Stripe sends payment related events to Subscribie via [`POST` requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST)- also known as 'webhooks').
If you're doing local development, then you need Stripe to send you the test payment events you're creating. `stripe cli` is a tool created by Stripe to do that. 

1. Install [Stripe cli](https://stripe.com/docs/stripe-cli#install)
2. Login into stripe via `stripe login` (this shoud open the browser with stripe page where you should enter your credentials). If this command doesn't work use `stripe login -i` (this will login you in interactive mode where instead of opening browser you'll have to put stripe secret key directly into terminal)
3. Run
  ``` 
  stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5000/stripe_webhook
   ```
   You will see:
   ```
   ⢿ Getting ready... > Ready! 
   ```
4. Please note, the stripe webhook secret is *not* needed for local development - for production, stripe webhook verification is done in  [Stripe-connect-webhook-endpoint-router](https://github.com/Subscribie/stripe-connect-webhook-endpoint-router) (you don't need this for local development). 
  ```
  stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5000/stripe_webhook
  ```
Remember Stripe will give you a key valid for 90 days, if you get the following error you will need to do step 2 again:

```
Error while authenticating with Stripe: Authorization failed, status=401
```
### Run browser automated tests with playright
> **Important:** Stripe cli must be running locally to recieve payment events:
>`stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5000/stripe_webhook`

<br />

#### Install Playwright dependencies
```
npm install
npm i -D @playwright/test
npx playwright install
npx playwright install-deps
```

Might see: `UnhandledPromiseRejectionWarning: browserType.launch: Host system is missing dependencies!`
```
  Install missing packages with:
      sudo apt-get install libgstreamer-plugins-bad1.0-0\
          libenchant1c2a
```

[Stripe-connect-account-announcer](https://github.com/Subscribie/stripe-connect-account-announcer)
needs to be running locally if you're runnning browser automated tests
locally.

#### Turn on headful mode & set Playwright host

```
export PLAYWRIGHT_HEADLESS=false
export PLAYWRIGHT_HOST=http://127.0.0.1:5000/
```

#### Run playwright tests:

```
cd tests/browser-automated-tests-playwright
npx playwright test
```
Something not working?
Debug playwright tests with the [playwright inspector](https://playwright.dev/docs/debug#playwright-inspector)
```
PWDEBUG=1 npx playwright test
```
If you don't see the playwright inspector, make sure you have an up to date version of playwright.

Alternative debugging with breakpoints

- Set breakpoint(s) by typing `debugger;` anywhere you want a breakpoint in a test.
Then run with the node debugger active:
```
unset PWDEBUG
node inspect index.js
```
Useful node debug commands:
- `help` # shows help
- `n` # go to next line
- `list()` # show code where paused
- `cont` # continue execution until next breakpoint
- 
##### For more information about test dependecies and how they work please go to [testing.md](https://github.com/Subscribie/subscribie/blob/master/testing.md)

# Logging & Debugging - How to change the logLevel
Quick: edit your `.env` file and set `PYTHON_LOG_LEVEL=DEBUG`.

E.g. to reduce the amount of logs, to `WARNING` or `CRITICAL`.

The default log level is `DEBUG` which means show as much logging
information as possible.

The possible values are DEBUG, INFO, WARNING, ERROR, CRITICAL
See https://docs.python.org/3/howto/logging.html

Flask *does* need to be restarted for the log level to change.


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

#### Locally
Locally you'll need to create public/private keys for secure
jwt authentication.

1) Generate public/private keys automatically

```
# Use the commands below to automaticaly create 'private.pem' file and key
openssl genrsa -out private.pem 2048
# Use this command to automatically generate your public.pem
openssl rsa -in private.pem -pubout > public.pem
```

2) Update .env file with PRIVATE_KEY and PUBLIC_KEY

```
PRIVATE_KEY="/path/to/private.pem"
PUBLIC_KEY="/path/to/public.pem"
```
## Logging in via jwt or basic auth

Provide the username & password in a POST request, and a jwt token is returned for 
use in further requests. 

# API Basics

## Oauth style login:

```
curl -v -d "username=admin@example.com" -d "password=password" http://127.0.0.1:5000/auth/jwt-login
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

## Get all plans

```
curl -v -H "Content-Type: application/json" -H "Authorization: Bearer <token> " http://127.0.0.1:5000/api/plans
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


# How new shops are created

1. New shop owner submits a form to create a new shop which hits `/start-building` endpoint
2. Shop is created and a new shop is started (Shop owner sees *"Please wait"*)
3. New Shop is ready
4. Shop owner is automatically redirected to the new shop, loged in using automated one-time login


# Saas Deployment

## Architecture

### Subscribie `shop`

Every shop owner gets a deployed flask application, with its own database.

### [`stripe-connect-account-announcer`](https://github.com/Subscribie/stripe-connect-account-announcer)

If a Subscribie `shop` connects to Stripe (it does not have to), then the `shop` will announce it's [Stripe connect id](https://stripe.com/docs/connect/authentication#stripe-account-header) to the `stripe-connect-account-announcer`.

The `stripe-connect-account-announcer` stores the Stripe connect id, so that when Stripe webhook events
arrive, the `stripe-connect-webhook-endpoint-router` knows which `shop` to send the events to. 

### [`stripe-connect-webhook-endpoint-router`](https://github.com/Subscribie/stripe-connect-webhook-endpoint-router)

A Stripe webhook endpoint.
Receives [Stripe webhook events](https://stripe.com/docs/webhooks#webhooks-def), which,

1. Inspects the [Stripe connect id](https://stripe.com/docs/connect/authentication#stripe-account-header) from the webhook request
2. Looks up the Stripe connect id (which has been stored by the `stripe-connect-account-announcer`)
3. Forwards the webhook event (e.g. [checkout-session-completed](stripe-connect-account-announcer)) to the correct Subscribie `shop`
4. The `shop` [verifies the webhook from Stripe](https://stripe.com/docs/webhooks/signatures), and processes the event.

> Note, in previous implementations there was one webhook endpoint per shop- this isn't compatible with Stripe when using Stripe Connect because there's a limmit on the number of webhooks, and connect events need to be routed based on their Stripe connect id anyway, hence the `stripe-connect-webhook-endpoint-router` performs this role.

#### Failure modes:

If the `stripe-connect-account-announcer` suffers an outage, this means new shops can't announce their Stripe account to `stripe-connect-webhook-endpoint-router` meaning, when a new Stripe event arrives from Stripe, then, Subscribie's `stripe-connect-webhook-endpoint-router` would not know which shop to send it to. Stripe [automatically retries the delivery of events](https://stripe.com/docs/webhooks/best-practices#retry-logic) which allows time for the system to recover in an outage.

## Application server: uwsgi

[uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) is used to run the application services.

Subscribie Saas uses the following key compoent of uwsgi: [Emperor mode](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html).

uWSGI **Emperor mode** starts and manages all running Subscribie shops as `uWSGI` vassals.

> "If the emperor dies, all the vassals die."<br />
   -[Emperor mode](https://uwsgi-docs.readthedocs.io/en/latest/Emperor.html)

<br />


<details>
  <summary>uWSGI - Emperor</summary>
  - When a new shop is created, the emperor notices a new shop, and starts it as a vassal.
  - Every Subscribie shop is a vassal of the emperor

</details>

<details>
  <summary>uWSGI - vassal-template</summary>
  - A vassal template is injected into every new shop by the emporor.
    - This avoids having to copy and paste the same config for every new shop.
    - It also means vassal config is in one place.
</details>
<br />
<br />


### Systemd services

<details>
<summary>subscribie</summary>
  The uWSGI emperor and the vassals it sawns is defined as a single systemd service called `subscribie`.
</details>


<details>
<summary>subscribie-deployer</summary>
  Responsible for listening for new Shop requests, and creating the Shop config which uWSGI needs to spawn a new Shop (aka uwsgi vassal).
</details>
<br />
<br />

### Optimisation

*Problem*: Every shop uses ~45mb of RAM. With lots of Shops the RAM usage can be high. Since shops are not receiving web traffic all the time we can stop them to reduce RAM usage.

*Solution*: uWSGI vassals are configured to be `OnDemandVassals` see [OnDemandVassals](https://uwsgi-docs.readthedocs.io/en/latest/OnDemandVassals.html)
and also socket-activated (note that's *two* different things):

*Result*: A reduction of > 17Gb of ram observed on a busy node.

- OnDemandVassals: The application is not started until the first request is received.
- Socket-activation: If running idle with no requests after x secconds, the shop is stoped- but is re-activated when a request comes in for the shop

Socker activation is enabled by using the uWSGI feature `emperor-on-demand-extension = .socket` in the `emperor.ini` config.

OnDemandVassals is enable by using the following config in the injected vassal config for every shop:

```
# idle time in seconds
idle = 60
# kill the application after idle time is reached
die-on-idle = true
```
See: [Combining on demand vassals with `--idle` and `--die-on-idle`](https://uwsgi-docs.readthedocs.io/en/latest/OnDemandVassals.html#combining-on-demand-vassals-with-idle-and-die-on-idle)

### Subscribie Saas other services

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

- Read through all these docs
- Submit a detailed [issue](https://github.com/Subscribie/subscribie/issues)


## Docker help

### How do I rebuild the container?
Sometimes you need to rebuild the container if you've made changes to the `Dockerfile`.
```
docker-compose up --build --force-recreate
```
