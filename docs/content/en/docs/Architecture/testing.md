---
title: "Testing"
date: 2022-11-09
weight: 2
description: >
  How to run Subscribie tests
---

> Subscribie uses [Playwright](https://playwright.dev/) for automated browser testing which tests most features at every pull request.


There are two types of test Subscribie has:
1. Browser automated tests using [playwright](https://github.com/microsoft/playwright)
2. Basic Python tests

# Run Basic Tests with `pytest`

```
. venv/bin/activate # activates venv
python -m pytest --ignore=node_modules # run pytest
```

# Browser automated tests with `playwright`

## Setup Playwright

#### Install Playwright dependencies
```
npm install
npm i -D @playwright/test
npx playwright install
npx playwright install-deps
```

> If you see: `UnhandledPromiseRejectionWarning: browserType.launch: Host system is missing dependencies!`
```
  Install missing packages with:
      sudo apt-get install libgstreamer-plugins-bad1.0-0\
          libenchant1c2a
```


#### Listen for Stripe webhooks locally

Stripe webhooks are recieved when payment events occur.
The test suite needs to listen to these events locally when running tests.

tldr: 
1. Install the stripe cli
2. Run `stripe listen --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed,payment_intent.payment_failed --forward-to 127.0.0.1:5000/stripe_webhook`

> For testing failed payments using [test cards table](https://stripe.com/docs/testing), the test card `4000000000000341` is especially useful because the cards in the previous table can’t be attached to a Customer object, but `4000000000000341` can be (and will fail which is useful for testing failed subscription payments such as `insufficient_funds`).

## Concept: What are [Stipe Webhooks](https://stripe.com/docs/webhooks)?
> Stripe takes payments. Stripe sends payment related events to Subscribie via [`POST` requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST)- also known as 'webhooks').
If you're doing local development, then you need Stripe to send you the test payment events you're creating. `stripe cli` is a tool created by Stripe to do that. 

1. Install [Stripe cli](https://stripe.com/docs/stripe-cli#install)
2. Login into stripe via `stripe login` (this shoud open the browser with stripe page where you should enter your credentials). If this command doesn't work use `stripe login -i` (this will login you in interactive mode where instead of opening browser you'll have to put stripe secret key directly into terminal)
3. Run
  ``` 
  stripe listen --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed --forward-to 127.0.0.1:5000/stripe_webhook
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

#### Bulk delete Stripe accounts

> **Warning**
> Stripe webhooks will be automatically disabled if error rates go above a certain %.
> To delete in bulk test Stripe Connect express accounts see: [./tests/delete_stripe_accounts_bulk.py](./tests/delete_stripe_accounts_bulk.py)


## Run Playwright tests
> **Important:** Stripe cli must be running locally to recieve payment events:
>`stripe listen --events checkout.session.completed,payment_intent.succeeded --forward-to 127.0.0.1:5000/stripe_webhook`

<br />



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
# Advanced Testing

> For more information about test dependecies and how they work please go to [testing.md](https://github.com/Subscribie/subscribie/blob/master/TESTING.md)
