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

  // Connect to Stripe via connect onboarding process
  await page.goto(PLAYWRIGHT_HOST + '/admin/connect/stripe-connect');
  await page.screenshot({ path: `connect-stripe-to-shop-dashboard-chromium.png` });

  // Check onboarding not already completed
  try {
    const contentSuccess = await page.textContent('.alert-success', {'timeout': 5000});
    if (contentSuccess.indexOf('Congrats!') > -1) {
      console.log("Already connected Stripe sucessfully, exiting test");
      await browser.close();
      return 0;
    }
  } catch (e) {
    console.log("Exception checking if onboarding completed, looks like it's not complete");
    console.log("Continuing anyway");
  }
  // Create shop owner strip connect email address based on 'admin' + 'hostname'
  const email = await page.evaluate(() => 'admin@' + document.location.hostname);

  await page.click('.btn.btn-success');
  await page.waitForNavigation({'timeout': 30000});

  // Click use the text phone number for SMS verification
  await page.click('text="the test phone number"');

  await page.fill('#email', email);
  await page.click('text="Next"');
  await page.click('text="Use test code"'); //Use Test code for SMS

  // Select Business details -> Industry as Software (needed again if repeating onboarding)
  try {
    await page.click('text="Please select your industry…"');
    await page.click('text="Software"');
    await page.click('text="Next"');
  } catch (e) {
    console.log("Exception when setting Industry - maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
  }

  // Try and select Sole Trader
  try {
    await page.click('#radio17', {'timeout': 5000}); // Sole trader
    await page.click('text="Next"');
  } catch (e) {
    console.log("Exception when setting Sole trader- maybe already completed this step");
    console.log(e);
  }

  // Fill personal details
  try {
    await page.fill('#first_name', "Sam");
    await page.fill('#last_name', "Smith");
    await page.fill('input[name=dob-day]', "28");
    await page.fill('input[name=dob-month]', "12");
    await page.fill('input[name=dob-year]', "1990");
    await page.fill('input[name=address]', "123 Tree Lane");
    await page.fill('input[name=locality]', "123 Tree Lane");
    await page.fill('input[name=zip]', "SW1A 1AA");
    await page.click('text="Next"');
  } catch (e) {
    console.log("Exception when setting personal details - maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
  }

  // Select Business details -> Industry as Software (needed if first time onboarding)
  try {
    await page.click('text="Please select your industry…"');
    await page.click('text="Software"');
    await page.click('text="Next"');
  } catch (e) {
    console.log("Exception when setting Industry - maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
  }

  // ID verification stage
  try {
    await page.click('text="Use test document"');
  } catch (e) {
    console.log("Exception when setting ID verification - maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
  }

  // Proof of address document stage
  try {
    await page.click('text="Use test document"');
  } catch (e) {
    console.log("Exception when performing Proof of address document stage - maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
  }

  // Payout details
  try {
    await page.click('text="Use test account"');
  } catch (e) {
    console.log("Exception when performing Payout details stage - maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
  }

  // Verification summary
  try {
    await page.click('button[data-db-analytics-name="connect_light_onboarding_action_requirementsIndexDone_button"]');
    await page.waitForNavigation({'timeout': 30000});
  } catch (e) {
    console.log("Exception in verivation summary done page- maybe already completed this step");
    console.log(e);
    console.log("Continuing regardless");
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

  await test_order_plan_with_subscription_and_upfront_charge(browsers, browserContextOptions);
  await clearDB();

  await test_order_plan_with_only_upfront_charge(browsers, browserContextOptions);
  await clearDB();

  await test_order_plan_with_only_recurring_charge(browsers, browserContextOptions);
  await clearDB();

  await test_order_plan_with_only_recurring_charge(browsers, browserContextOptions);
  await clearDB();
})();
