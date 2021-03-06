require('dotenv').config()

test_order_plan_with_subscription_and_upfront_charge = require('./tests/test_order_plan_with_subscription_and_upfront_charge');
test_order_plan_with_only_upfront_charge = require('./tests/test_order_plan_with_only_upfront_charge');
test_order_plan_with_only_recurring_charge = require('./tests/test_order_plan_with_only_recurring_charge');
test_transaction_filter_by_name_and_by_plan_title = require('./tests/test_transaction_filter_by_name_and_by_plan_title');
const playwright = require('playwright');
const fs = require('fs');
const { devices } = require('playwright');
const iPhone = devices['iPhone 11'];
const assert = require('assert');
const DEFAULT_TIMEOUT = 40000;
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

async function handle_dialog(dialog) {
    console.log(dialog.message);
    await dialog.dismiss()
}

// Connect to stripe connect using test/fake sms as we're in test mode
async function test_connect_to_stripe_connect()  {

  console.log("test_connect_to_stripe_connect");
  const browser = await playwright['chromium'].launch({headless: PLAYWRIGHT_HEADLESS});
  const context = await browser.newContext(browserContextOptions);
  context.setDefaultTimeout(DEFAULT_TIMEOUT);
  const page = await context.newPage();
  page.on("dialog", handle_dialog)

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
  await page.goto(PLAYWRIGHT_HOST + 'admin/connect/stripe-connect');
  await page.screenshot({ path: `connect-stripe-to-shop-dashboard-chromium.png` });
  // Check onboarding not already completed
  try {
    context.setDefaultTimeout(3000);
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
  context.setDefaultTimeout(5000);
  // Start Stripe connect onboarding
  await page.goto(PLAYWRIGHT_HOST + 'admin/connect/stripe-connect');
  await page.click('.btn-success');
  await detect_stripe_onboarding_page()

  async function detect_stripe_onboarding_page() {
    console.log("Start Stripe connect onboarding")
    try {
      let contentStripePage = await page.evaluate(() => document.body.textContent);
 
      // Stripe onboarding login
      if ( contentStripePage.indexOf("Get paid by Subscribie") > -1 ) {
        console.log("Detected stripe onboarding")
        // Use the text phone number for SMS verification
        await page.click('text="the test phone number"');
        await page.fill('#email', email);
        await page.click('text="Next"');
        await page.click('text="Use test code"'); //Use Test code for SMS
      } else {
        console.log("Could not detect stripe onboarding page")
      }

      // Use SME verify with test code
      if ( contentStripePage.indexOf("Enter the verification code we sent") > -1 ) {
        console.log("Clicking Use test code")
        await page.click('text="Use test code"'); //Use Test code for SMS
      }


      // Stripe onboarding Business type
      if (contentStripePage.indexOf('Type of business') > -1 ) {
        await new Promise(x => setTimeout(x, 4000));
        await page.selectOption('select', 'individual');
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
      if (contentStripePage.indexOf('Tell us about Soap Subscription') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Please select your industry…"');
        await page.click('text="Software"');
        await page.click('text="Next"');
      }

      // Stripe onboarding payouts bank details
      if (contentStripePage.indexOf('Select an account for payouts') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Use test account"');
      }

      // Stripe ID & Home Address verification
      if (contentStripePage.indexOf("Missing required information") > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Update"');
      }
       
      // Stripe onboarding identify verification step
      if (contentStripePage.indexOf('ID verification') > -1 ) {
        await page.pause();
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button:has-text("Use test document")');
      }

      //Stripe onboarding address verification step
      if (contentStripePage.indexOf("Verify home address") > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button[data-db-analytics-name="connect_light_onboarding_action_documentTrigger_button"]');
      }
      if (contentStripePage.indexOf("Proof of address document") > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Use test document"');
      }

      //Stripe Done ID & Home verification
      if (contentStripePage.indexOf("Additional information") > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button[data-db-analytics-name="connect_light_onboarding_action_personFormSubmit_button"]');
      }

      // Verify now in first flow
      if (contentStripePage.indexOf("Verify now") > -1 ) {
        await page.pause();
        await new Promise(x => setTimeout(x, 1000));
        await page.waitForNavigation({'timeout': 3000});
      }

      // ID verification use test document
      if (contentStripePage.indexOf("ID verification for Sam Smith") > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Use test document"');
        await page.waitForNavigation({'timeout': 3000});
      }
      // Stripe onboarding verification summary
      if (contentStripePage.indexOf("Please double-check that this information is correct") > -1 ) {
        console.log("On the Let's review your details page");
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button:has-text("Done")');
        await page.waitForNavigation({'timeout': 3000});
      }

      // Stripe onboarding verification complete
      if (contentStripePage.indexOf('Your verification is complete') > -1 ) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('button[data-db-analytics-name="connect_light_onboarding_action_requirementsIndexDone_button"]');
        //await page.waitForNavigation({'timeout': 30000});
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

  await clearDB();
  await test_order_plan_with_subscription_and_upfront_charge(browsers, browserContextOptions);
  await test_transaction_filter_by_name_and_by_plan_title(browsers, browserContextOptions);
  
  await clearDB();
  await test_order_plan_with_only_upfront_charge(browsers, browserContextOptions);
  await clearDB();

})();
