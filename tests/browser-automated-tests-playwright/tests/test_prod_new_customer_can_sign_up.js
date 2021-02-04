const playwright = require('playwright');
const fs = require('fs');
const { devices } = require('playwright');
const iPhone = devices['iPhone 11'];
const assert = require('assert');
const DEFAULT_TIMEOUT = 10000
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const videosDir = __dirname + '/videos/';
const videoWidth = 1280
const videoHeight = 720;
const browserContextOptions = {...iPhone, recordVideo: { dir: videosDir, size: {width: videoWidth, height: videoHeight} }}


const browsers = ['chromium'];

/* Test an order can be placed for a plan with only an upfront payment */
async function test_prod_new_customer_can_sign_up(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_prod_new_customer_can_sign_up");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(DEFAULT_TIMEOUT);
    const page = await context.newPage();

    // Go to homepage and start signing up
    var epoch = Math.floor(+new Date() / 1000);
    await page.goto("http://subscriptionwebsitebuilder.co.uk/");
    await page.screenshot({ path: `prod-sign-up-landingpage-${browserType}.png` });
    
    await page.click('text="Start now"');
    await page.screenshot({ path: `prod-sign-up-start-now-page-${browserType}.png` });

    // Fill in sign-up form (Getting started form)
    await page.fill('#email', 'prod-test-' + epoch + '@example.com');
    await page.fill('#company_name', 'prod-test-' + epoch);
    await page.fill('#password', 'prod-test-' + epoch);

    await page.screenshot({ path: `prod-sign-up-getting-started-page-${browserType}.png` });

    // Enter a plan
    await page.fill('#title-0', 'prod-test-' + epoch);
    await page.fill('#interval_amount-0', "5.99");
    await page.fill('#selling_points-0-0', "A. The best");
    await page.fill('input[name=selling_points-0-1]', "B. New every month");
    await page.fill('input[name=selling_points-0-2]', "C. Fast");

    await page.screenshot({ path: `prod-sign-up-entered-plan-${browserType}.png` });

    // Start site build process
    await page.click('text="Save"');

    await page.screenshot({ path: `prod-sign-up-plan-choice-${browserType}.png` });

    // Choose the first plan (sign up)
    await page.click('text="Choose"');

    await page.screenshot({ path: `prod-sign-up-enter-shop-owner-details-${browserType}.png` });

    // Fill in sign-up form (shop owner info)
    await page.fill('#given_name', 'prod-test-fname' + epoch);
    await page.fill('#family_name', 'prod-test-lname' + epoch);
    await page.fill('#email', 'prod-test-' + epoch + '@example.com');
    await page.fill('#address_line_one', 'prod-test-' + epoch + 'address-line-1');
    await page.fill('#city', 'prod-test-' + epoch + '-london');
    await page.fill('#postcode', 'prod-test-' + epoch);

    await page.screenshot({ path: `prod-sign-up-enterd-shop-owner-details-${browserType}.png` });

    //Proceed to order summary page
    await page.click('text="Next Step"');

    await page.screenshot({ path: `prod-sign-up-view-order-summary-${browserType}.png` });

    // Proced to stripe checkout
    await page.click('text="Checkout"');

    await page.screenshot({ path: `prod-sign-up-reached-stripe-checkout-${browserType}.png` });

    await browser.close();
  }
};

module.exports = test_prod_new_customer_can_sign_up;

(async() => {
  await test_prod_new_customer_can_sign_up(browsers, browserContextOptions);
})();

