const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

/* Test an order can be placed for a plan with subscription & upfront payment */
async function test_order_plan_with_subscription_and_upfront_charge(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_order_plan_with_subscription_and_upfront_charge");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(15000);
    const page = await context.newPage();
    
    // Login and verify order appears in admin dashboard
    // Login
    await page.goto(PLAYWRIGHT_HOST + 'auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    await page.screenshot({ path: `logged-in-${browserType}.png` });
    // Assert logged in OK
    const content = await page.textContent('.card-title')
    assert(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
    
    // Verify transaction is present in 'All transactions page'
    await page.goto(PLAYWRIGHT_HOST + 'admin/transactions')
    await page.screenshot({ path: `view-transactions-${browserType}.png` });
    const transaction_content = await page.textContent('.transaction-amount');
    assert (transaction_content == '£6.99');

    // Verify subscriber is linked to the transaction:
    const transaction_subscriber_content = await page.textContent('.transaction-subscriber');
    assert (transaction_subscriber_content === 'John smith');
      // Verify search by Name - Transaccions
    await page.fill('input[name=subscriber_name]',"John");
    await page.click('.btn-primary');
    assert (transaction_subscriber_content === 'John smith');

      // Verify search by plan title 
    await page.fill('input[name=plan_title]',"Hair");
    await page.click('.btn-primary');
    assert (transaction_subscriber_content === 'John smith');

      // Verify search by Name & plan title
    await page.fill('input[name=subscriber_name]',"John");
    await page.fill('input[name=plan_title]',"Hair");
    await page.click('.btn-primary');
    assert (transaction_subscriber_content === 'John smith');

    // Logout of shop owners admin dashboard
    await page.goto(PLAYWRIGHT_HOST + 'auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    assert(logged_out_content === "You have logged out");
 
    await browser.close();
  }
};

module.exports = test_order_plan_with_subscription_and_upfront_charge
