const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

/* Test transactions can be query by plan title and name */
async function test_pause_resume_active_subscriptions(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_pause_cancel_active_subscriptions");
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
    
    // Go to My Subscribers page
    // Crude wait before we check subscribers to allow webhooks time
    await new Promise(x => setTimeout(x, 1000)); // 5 secconds
    await page.goto(PLAYWRIGHT_HOST + 'admin/subscribers')
    await page.screenshot({ path: `view-subscribers-${browserType}.png` });

    // Verify that subscriber is present in the list
    const subscriber_email_content = await page.textContent('.subscriber-email');
    assert(subscriber_email_content === 'john@example.com');

    const subscriber_subscription_title_content = await page.textContent('.subscription-title');
    assert(subscriber_subscription_title_content === 'Hair Gel');
    
    // Verify if subscription active & click cancel 
    const subscription_status = await page.textContent('.subscription-status');
    assert(subscription_status === "active");
    
    //Pause Subscription
    await page.click('.pause-action');
    const subscription_pause_notification = await page.textContent('text="Subscription paused"');
    assert(subscription_pause_notification === "Subscription paused");

    await new Promise(x => setTimeout(x, 3000)); // 3 secconds
    
    //Resume Subscription
    await page.click('.resume-action');
    const subscription_resume_notification = await page.textContent('text="Subscription resumed"');
    assert(subscription_resume_notification === "Subscription resumed");
 
    // Logout of shop owners admin dashboard
    await page.goto(PLAYWRIGHT_HOST + 'auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    assert(logged_out_content === "You have logged out");
 
    await browser.close();
  }
};

module.exports = test_pause_resume_active_subscriptions
