# Testing Subscribie
## Automated browser testing using Playwright 

File name structure: 

### Worker Name--Issue Number-User Based-Test Name

The worker name example, test.spec, worker1.spec, worker2.spec. The spec is necessary to be assimilated as another worker. 
Tags (@) are used to filter tests by issue number, user based (owner-shop, subscriber) and test name.
To run only the specified tests, the syntax is:
**These examples can be used locally or in github actions.

npx playwright test --grep @issue-numer/User Based/Test Name --update-snapshots
Examples:
```
npx playwright test --grep @704 --update-snapshots # run only tests for issue #704
```
```
npx playwright test --grep @subscriber --update-snapshots # runs all subscriber tests
```
```
npx playwright test --grep @plan_creation --update-snapshots # run only plan creation test
```

To exclude specific tests: 
npx playwright test --grep-invert @issue-numer/User Based/Test Name --update-snapshots.

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

* Before each test, playwright logs in with a shop-owner user. 

* Stripe test: Check if stripe is connected, otherwise connect to stripe. (this is the longest tests 3minutes if not connected)

* order_plan_with_only_recurring_charge

* order_plan_with_only_upfront_charge 

* Order_plan_with_free_trial

  * Order_plan_with_subscription_and_upfront_charge

  * Transaction filter by name and plan title
 
  * pause, resume subscription test

  * cancel subscription test.
 
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

Worker 3 mostly contains tests that don't require stripe to be connected, only the last one (ordering plan with vat) requires Stripe to be connected. 

# TEST RELATIONSHIP

<img width="799" alt="Screen Shot 2021-09-20 at 11 53 29 PM" src="https://user-images.githubusercontent.com/76879536/134396271-f4382aba-50ca-47e7-b2e0-1dbae51397e4.png">





























