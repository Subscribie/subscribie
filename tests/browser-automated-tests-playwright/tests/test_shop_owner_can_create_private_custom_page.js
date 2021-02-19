const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

async function test_shop_owner_can_create_private_custom_page(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_shop_owner_can_create_private_custom_page");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(15000);
    const page = await context.newPage();

    await page.goto(PLAYWRIGHT_HOST);
    // Close page
    await page.close();

  }
};

module.exports = test_shop_owner_can_create_private_custom_page;
