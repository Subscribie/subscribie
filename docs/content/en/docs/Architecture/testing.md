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
1. Install the Stripe cli
2. Run `stripe listen --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed,payment_intent.payment_failed --forward-to 127.0.0.1:5000/stripe_webhook`

> For testing failed payments using [test cards table](https://stripe.com/docs/testing), the test card `4000000000000341` is especially useful because the cards in the previous table can’t be attached to a Customer object, but `4000000000000341` can be (and will fail which is useful for testing failed subscription payments such as `insufficient_funds`).

## [Stripe Webhooks](https://stripe.com/docs/webhooks)
> Stripe takes payments. Stripe sends payment related events to Subscribie via [`POST` requests](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST)- also known as 'webhooks').
If you're doing local development, then you need Stripe to send you the test payment events you're creating. `stripe cli` is a tool created by Stripe to do that. 

1. Install [Stripe cli](https://stripe.com/docs/stripe-cli#install)
2. Login into stripe via `stripe login` (this shoud open the browser with stripe page where you should enter your credentials). If this command doesn't work use `stripe login -i` (this will login you in interactive mode where instead of opening browser you'll have to put Stripe secret key directly into terminal)
3. Run
  ``` 
  stripe listen --events checkout.session.completed,payment_intent.succeeded,payment_intent.payment_failed --forward-to 127.0.0.1:5000/stripe_webhook
   ```
   You will see:
   ```
   ⢿ Getting ready... > Ready! 
   ```
4. Please note, the stripe webhook secret is *not* needed for local development - for production, Stripe webhook verification is done in  [Stripe-connect-webhook-endpoint-router](https://github.com/Subscribie/stripe-connect-webhook-endpoint-router) (you don't need this for local development). 
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

## Advanced Playwright Testing

You can run individual playwright tests by:

- Tags: `@` are used to run tests by issue number
- User based (`shop-owner`, `subscriber`) 
- Test name

For example, you may want to run only tests which impact the `shop-owner`

> The test file name structure is `Worker Name--Issue Number-User Based-Test Name`

### Examples to run a specific Playwright test:

```
npx playwright test --grep @issue-numer/User Based/Test Name --update-snapshots

```

For example:


Run only tests for issue #704

```
npx playwright test --grep @704 --update-snapshots
```


Run all subscriber tests:

```
npx playwright test --grep @subscriber --update-snapshots
```


Run only plan creation tests:
```
npx playwright test --grep @plan_creation --update-snapshots
```

To exclude specific test, but run all others:

```
npx playwright test --grep-invert @issue-numer/User Based/Test Name --update-snapshots.
```

### How playwright workers work


The workers are specified in the playwright.config.ts file. 
Which is the file containing the global settings for the playwright tests:

* The working directories
* Global time out 3mins before each test is retried 
* Retry 2 times if a test fails
* How many workers(parallel jobs playwright can do) at the same time. We have 3
* Headless config on/off depending in the .env variable if true or false 
  * SlowMo specified in the env (miliseconds)
  * baseURL, specified in the env. Ex 127.0.0.1
  * Video Recording

Using Chromium because headless only works in chromium not mobile

#### Worker 1 is called index.spec.js (it can be called any name but needs to end in .spec.)
In worker 1 we have these tests: 

* Before each test, playwright logs in with a `shop-owner` user. 

* Stripe test: Check if Stripe is connected, otherwise connect to Stripe. (this is the longest tests 3minutes if not connected)

* order_plan_with_only_recurring_charge

* order_plan_with_only_upfront_charge 

* Order_plan_with_free_trial

  * Order_plan_with_subscription_and_upfront_charge

  * Transaction filter by name and plan title
 
  * pause, resume subscription test

  * cancel subscription test.
  
  * Subscriber filter by name and plan title
 
#### Worker2 is called worker2.spec.js and in this worker have these tests:
 * plan_creation
  
 * changing_plans_order
  
 * share_private_plan_url 
  
 * order_plan_with_choice_options_and_required_note
  
 * order_plan_with_cancel_at
  
 * order_plan_cooling_off

Why these tests? plan creation, changing plans order, and sharing private plan url do not depend on the  previous tests so while Worker 1, Stripe Connect, test is running (takes 3min to complete) this worker is running those 3 tests first. By the time those 3 tests are run, tripe is already connected and we can start doing tests that require Stripe to be connected like ordering plans. 

#### Worker 3 is called worker3.spec.js and this worker has these tests:
  * clear_DB
  
 * categories_creation 
  
 * private_page_creation 
  
 * Public_page_creation
  
 * Slogan_creation
  
 * Change_shop_colour
  
 * Adding_vat
  
 * ordering_plan_with_VAT
 
 * subscriber_magic_login
 
 * subscriber_order_free_plan
 * subscriber_change_card_details

Worker 3 mostly contains tests that don't require Stripe to be connected, only the 4th last ones requires Stripe to be connected.

The worker name example, test.spec, worker1.spec, worker2.spec. 

The spec is necessary for the tests to be discovered by Playwright as another worker.

To run only the specified tests, the syntax is:

# TEST RELATIONSHIP
![Subscribie Playwright tests drawio](https://user-images.githubusercontent.com/76879536/200958357-621ae5ee-6084-4e2f-999c-42731dab102d.png)
