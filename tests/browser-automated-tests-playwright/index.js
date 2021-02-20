require('dotenv').config()

test_order_plan_with_subscription_and_upfront_charge = require('./tests/test_order_plan_with_subscription_and_upfront_charge');
test_order_plan_with_only_upfront_charge = require('./tests/test_order_plan_with_only_upfront_charge');
test_order_plan_with_only_recurring_charge = require('./tests/test_order_plan_with_only_recurring_charge');

const playwright = require('playwright');
const fs = require('fs');
const { devices } = require('playwright');
const iPhone = devices['iPhone 11'];
const assert = require('assert');
const DEFAULT_TIMEOUT = 10000;
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const videosDir = __dirname + '/videos/';
const videoWidth = 1280
const videoHeight = 720;
const browserContextOptions = {...iPhone, recordVideo: { dir: videosDir, size: {width: videoWidth, height: videoHeight} }}

//const browsers = ['chromium', 'webkit'];
const browsers = ['chromium'];


// Delete any existing persons & subscriptions from the database
async function clearDB() {
  const browser = await playwright['chromium'].launch({headless: PLAYWRIGHT_HEADLESS});
  const context = await browser.newContext(browserContextOptions);
  const page = await context.newPage();

  // Login then clearDB
  await page.goto(PLAYWRIGHT_HOST + 'auth/login');
  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'password');
  await page.click('#login');

  await page.goto(PLAYWRIGHT_HOST + '/admin/remove-subscriptions');
  const contentSubscriptions = await page.evaluate(() => document.body.textContent.indexOf("all subscriptions deleted"));
  assert(contentSubscriptions > -1);

  await page.goto(PLAYWRIGHT_HOST + '/admin/remove-people');
  const contentPeople = await page.evaluate(() => document.body.textContent.indexOf("all people deleted"));
  assert(contentPeople > -1);

  await page.goto(PLAYWRIGHT_HOST + '/admin/remove-transactions');
  const contentTransactions = await page.evaluate(() => document.body.textContent.indexOf("all transactions deleted"));
  assert(contentTransactions > -1);

  await browser.close();
}

async function saveVideo(filename) {
  const currentVideoFile = fs.readdirSync(videosDir).find(name => name.endsWith('webm'));
  console.log("The current file is:");
  console.log(currentVideoFile);
  await new Promise(x => setTimeout(x, 1000));
  //await fs.copyFileSync(videosDir + currentVideoFile, videosDir + filename + currentVideoFile);
}



// Connect to stripe connect using test/fake sms as we're in test mode
async function test_connect_to_stripe_connect()  {

  console.log("test_connect_to_stripe_connect");
  const browser = await playwright['chromium'].launch({headless: PLAYWRIGHT_HEADLESS});
  const context = await browser.newContext(browserContextOptions);
  context.setDefaultTimeout(10000);
  const page = await context.newPage();

  // Login
  await page.goto(PLAYWRIGHT_HOST + 'auth/login');
  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'password');
  await page.click('#login');
  await page.screenshot({ path: `logged-in-chromium.png` });
  // Assert logged in OK
  const content = await page.textContent('.card-title')
  assert(content === 'Checklist'); // If we see "Checklist", we're logged in to admin

  // Go to Stripe Connect payment gateways page
  await page.goto(PLAYWRIGHT_HOST + '/admin/connect/stripe-connect');
  await page.screenshot({ path: `connect-stripe-to-shop-dashboard-chromium.png` });

  // Check onboarding not already completed
  try {
    const contentSuccess = await page.textContent('.alert-success');
    if (contentSuccess.indexOf('Congrats!') > -1) {
      console.log("Already connected Stripe sucessfully, exiting test");
      await browser.close();
      return 0;
    }
  } catch (e) {
    console.log("Exception checking if onboarding completed, looks like it's not complete");
    console.log("Continuing with Stripe Connect onboarding");
  }

  // Create shop owner stripe connect email address based on 'admin' + 'hostname'
  const email = await page.evaluate(() => 'admin@' + document.location.hostname);

  // Start Stripe connect onboarding
  await page.click('.btn.btn-success');
  await page.waitForNavigation({'timeout': 30000});

  async function detect_stripe_onboarding_page() {
    try {
      let contentStripePage = await page.evaluate(() => document.body.textContent);
 
      // Stripe onboarding login
      if ( contentStripePage.indexOf("Subscribie partners with Stripe for fast") > -1 ) {
        // Use the text phone number for SMS verification
        await page.click('text="the test phone number"');
        await page.fill('#email', email);
        await page.click('text="Next"');
        await page.click('text="Use test code"'); //Use Test code for SMS
      }

      // Stripe onboarding Business type
      if (contentStripePage.indexOf('Type of business') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.selectOption('#Select17', 'individual');
        await page.click('text="Next"');
      }

      // Stripe onboarding Type of entity
      // (sometimes a dropdown is shown, sometimes a radio selection
      if (contentStripePage.indexOf('Type of entity') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.check('input[name="business_type"][value="individual"]');
        await page.click('text="Next"');
      }
      
      // If on the document verification page, only email and phone number needed to login
      // so press next. This is confusing because "Tell us a few details about yourself" also
      // appears on an earlier onboarding step (before doing document verification)
      if (contentStripePage.indexOf('Tell us a few details about yourself') > -1)
      {
        let numInputs = await page.evaluate(() => document.forms[0].querySelectorAll('input').length);
        if (numInputs == 2) {
            await page.click('text="Next"');
        }
      }

      // Stripe onboarding personal details step
      if (contentStripePage.indexOf('Tell us a few details about yourself') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        try {
            await page.fill('#first_name', "Sam");
            await page.fill('#last_name', "Smith");
            await page.fill('input[name=dob-day]', "28");
            await page.fill('input[name=dob-month]', "12");
            await page.fill('input[name=dob-year]', "1990");
        } catch (e) {
          console.log("Exception in setting personal details, perhaps already completed");
          console.log(e);
          console.log("Continuing regardless");
        }
        await page.fill('input[name=address]', "123 Tree Lane");
        await page.fill('input[name=locality]', "123 Tree Lane");
        await page.fill('input[name=zip]', "SW1A 1AA");
        await page.click('text="Next"');
      }


      // Stripe onboarding industry selection
      if (contentStripePage.indexOf('Tell us about Soap Subscription.') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Please select your industry…"');
        await page.click('text="Software"');
        await page.click('text="Next"');
      }


      // Stripe onboarding identify verification step
      if (contentStripePage.indexOf('ID verification for Sam Smith') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Use test document"');
      }


      // Stripe onboarding payouts bank details
      if (contentStripePage.indexOf('Tell us where you’d like to receive your payouts.') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Use test account"');
      }


      // Stripe onboarding verification summary
      if (contentStripePage.indexOf('almost ready to start getting paid by Subscribie.') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button[data-db-analytics-name="connect_light_onboarding_action_requirementsIndexDone_button"]');
        //await page.waitForNavigation({'timeout': 30000});
      }


      // Stripe onboarding verification complete
      if (contentStripePage.indexOf('Your verification is complete') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button[data-db-analytics-name="connect_light_onboarding_action_requirementsIndexDone_button"]');
        //await page.waitForNavigation({'timeout': 30000});
      }


      // Stripe onboarding proof of address
      if (contentStripePage.indexOf('Proof of address') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));

      }


      // Stripe onboarding go back to onboarding if incomplete
      if (contentStripePage.indexOf('Payouts to your bank account are not active yet') > -1 ) {
        await page.click('.btn.btn-success');
        await page.waitForNavigation({'timeout': 30000});
      }

    } catch (e) { 
      console.log(e);
      console.log("Retrying onboarding steps");
    }

    // If Stripe onboarding not complete, retry

    try {
      let pageBody = await page.evaluate(() => document.body.textContent);
      if (pageBody.indexOf('Congrats! Payouts are active on your site') == -1) {
        await detect_stripe_onboarding_page();
      }
    } catch (e) {
        console.log(e);
        await detect_stripe_onboarding_page();
    }
  }

  await detect_stripe_onboarding_page();
  
  console.log("Announce stripe account manually visiting announce url. In prod this is called via uwsgi cron");
  await page.goto(PLAYWRIGHT_HOST + '/admin/announce-stripe-connect');
  const contentStripeAccountAnnounced = await page.evaluate(() => document.body.textContent.indexOf("Announced Stripe connect account"));
  assert(contentStripeAccountAnnounced > -1);

  await browser.close();

}


(async() => {
  await clearDB();
  await test_connect_to_stripe_connect();

  await clearDB();
  await test_order_plan_with_only_recurring_charge(browsers, browserContextOptions);

  await test_order_plan_with_subscription_and_upfront_charge(browsers, browserContextOptions);
  await clearDB();

  await test_order_plan_with_only_upfront_charge(browsers, browserContextOptions);
  await clearDB();

})();
