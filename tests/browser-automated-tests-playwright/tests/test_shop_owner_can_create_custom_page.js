const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

async function test_shop_owner_can_create_custom_page(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_can_create_custom_page");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(15000);
    const page = await context.newPage();

    console.log("Login as shop owner");
    await page.goto(PLAYWRIGHT_HOST + '/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    await page.screenshot({ path: `logged-in-${browserType}.png` });

    console.log("Go to dashboard");
    await page.goto(PLAYWRIGHT_HOST + '/admin/dashboard');

    console.log("Click Modules");
    await page.click('text="Modules"');

    await page.click('"List pages"'); 
    await page.screenshot({ path: `on-list-custom-pages-page-${browserType}.png` });

    await page.click('"Add page"');
    await page.screenshot({ path: `on-add-custom-page-page-${browserType}.png` });

  
    console.log("Fill out page title");
    await page.fill('#page-title', "custom page");

    await page.fill('.note-editable', "This is my custom page");
    await page.screenshot({ path: `filled-in-new-custom-page-${browserType}.png` });
    await page.click('"Save"');

    console.log("Verify 'Your new page custom page has been created' is in response");

    const new_page_created_content = await page.textContent('.alert-primary');
    await page.screenshot({ path: `new-custom-page-confirmation-${browserType}.png` });
    assert(new_page_created_content.includes("custom page has been created") === true);

    console.log("Click link to custom page");
    await page.click('"custom page"');
    await page.screenshot({ path: `visit-custom-page-${browserType}.png` });

    console.log("Verify custom page content is 'This is my custom page'");
    const new_page_content = await page.textContent('body');
    assert(new_page_content.includes("This is my custom page"));

    await browser.close();
  }
};

module.exports = test_shop_owner_can_create_custom_page;
