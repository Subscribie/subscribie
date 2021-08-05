const playwright = require('playwright');
const fs = require('fs');
const { devices } = require('playwright');
const iPhone = devices['iPhone 11'];
const assert = require('assert');
const DEFAULT_TIMEOUT = 500000
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const videosDir = __dirname + '/videos/';
const videoWidth = 1280
const videoHeight = 720;
const browserContextOptions = {...iPhone, recordVideo: { dir: videosDir, size: {width: videoWidth, height: videoHeight} }}


const browsers = ['chromium'];

/* Test Google signin step one workd (presented with google login 
   Does NOT test if full login with Google works, only that the oauth
   client (client id and permitted origins are correct)
*/
async function test_prod_google_oauth_step_one_works(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_prod_can_visit_google_signin_page");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(DEFAULT_TIMEOUT);
    const page = await context.newPage();

    // Go to google signin route
    await page.goto("https://subscriptionwebsitebuilder.co.uk/withgoogle");
    await page.screenshot({ path: `prod-visit-google-login-signin-${browserType}.png` });
    
    await browser.close();
  }
};

module.exports = test_prod_google_oauth_step_one_works;

(async() => {
  await test_prod_google_oauth_step_one_works(browsers, browserContextOptions);
})();

