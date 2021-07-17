const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

/* Test transactions can be query by plan title and name */
async function test_transaction_refund(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_transaction_refund");
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
    
    // Verify transaction is paid in 'All transactions page'
    await page.goto(PLAYWRIGHT_HOST + 'admin/transactions')
    await page.screenshot({ path: `view-transactions-${browserType}.png` });

    const transaction_content = await page.textContent('.payment-status');
    assert (transaction_content === 'paid');

    // click refund transaction
    await page.click('.refund-action');
    await new Promise(x => setTimeout(x, 2000)); //5 secconds

    //Click yes refund transaction 
    await page.click('.btn-danger')
    await new Promise(x => setTimeout(x, 2000)); //5 secconds

    // Verify subscriber is linked to the transaction:
    const transaction_content_refund = await page.textContent('.refund-status');
    assert (transaction_content_refund === 'Refunded');

    // Logout of shop owners admin dashboard
    await page.goto(PLAYWRIGHT_HOST + 'auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    assert(logged_out_content === "You have logged out");
 
    await browser.close();
  }
};

module.exports = test_transaction_refund
