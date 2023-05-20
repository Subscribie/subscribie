const playwright = require('playwright');
const fs = require('fs');
const { devices } = require('playwright');
const iPhone = devices['iPhone 11'];
const assert = require('assert');
const DEFAULT_TIMEOUT = 500000
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;;
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
    
    await page.click('text="Get Started"');
    await page.screenshot({ path: `prod-sign-up-start-now-page-${browserType}.png` });


    // Fill in sign-up form (Getting started form)
    await page.fill('#email', 'prod-test-' + epoch + '@example.com');
    await page.fill('#company_name', 'prod-test-' + epoch);
    await page.fill('#password', 'prod-test-' + epoch);

    await page.screenshot({ path: `prod-sign-up-getting-started-page-${browserType}.png` });

    // Enter a plan
    await page.fill('#title-0', 'prod-test-' + epoch);

    await page.screenshot({ path: `prod-sign-up-entered-plan-${browserType}.png` });

    // Start site build process
    await page.click('text="Save"');

    await page.screenshot({ path: `prod-sign-up-plan-choice-${browserType}.png` });


    // Verify new site has come online ok
    await new Promise(x => setTimeout(x, 20000)); //Allow 20 secconds for new site to boot
    await page.goto("https://" + 'prodtest' + epoch + ".subscriby.shop");
    const new_shop_category_title_content = await page.textContent('.title-1');
    assert(new_shop_category_title_content === 'prod-test-' + epoch)
    await browser.close();
  }
};

module.exports = test_prod_new_customer_can_sign_up;

(async() => {
  await test_prod_new_customer_can_sign_up(browsers, browserContextOptions);
})();

