const playwright = require('playwright');
const assert = require('assert');
const DEFAULT_TIMEOUT = 10000
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

/* Test an order can be placed for a plan with only an upfront payment */
async function test_order_plan_with_only_upfront_charge(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_order_plan_with_only_upfront_charge");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(DEFAULT_TIMEOUT);
    const page = await context.newPage();

    // Buy item with subscription & upfront fee
    await page.goto(PLAYWRIGHT_HOST); // Go to home before selecting product
    await page.goto(PLAYWRIGHT_HOST + '/new_customer?plan=58921f7a-3371-4ccf-aeee-e2b8af5cca3a');

    // Fill in order form
    await page.fill('#given_name', 'John');
    await page.fill('#family_name', 'Smith');
    await page.fill('#email', 'john@example.com');
    await page.fill('#mobile', '07123456789');
    await page.fill('#address_line_one', '123 Short Road');
    await page.fill('#city', 'London');
    await page.fill('#postcode', 'L01 T3U');
    await page.screenshot({ path: `new-customer-form-${browserType}.png` });
    await page.click('text="Continue to Payment"');
    await page.screenshot({ path: `begin-payment-step-${browserType}.png` });
    // Begin stripe checkout
    await page.screenshot({ path: `pre-stripe-checkout-${browserType}.png` });
    await page.click('#checkout-button');

    //Verify first payment is correct (upfront charge + first recuring charge)
    const first_payment_content = await page.textContent('#ProductSummary-totalAmount');
    assert(first_payment_content === "£5.66");
    const upfront_charge_content = await page.textContent('.Text-fontSize--16');
    assert(upfront_charge_content === "One-Off Soaps");

    // Pay with test card
    await page.fill('#cardNumber', '4242 4242 4242 4242');
    await page.fill('#cardExpiry', '04 / 24');
    await page.fill('#cardCvc', '123');
    await page.fill('#billingName', 'John Smith');
    await page.selectOption('select#billingCountry', 'GB');
    await page.fill('#billingPostalCode', 'LN1 7FH');
    await page.screenshot({ path: `stripe-checkout-filled-in-${browserType}.png` });
    await page.click('.SubmitButton');
  
    // Verify get to the thank you page order complete
    context.setDefaultTimeout(30000);
    const order_complete_content = await page.textContent('.title-1');
    assert(order_complete_content === "Order Complete!");
    await page.screenshot({ path: `order-complete-${browserType}.png` });
    
    // Login and verify order appears in admin dashboard
    // Login
    await page.goto(PLAYWRIGHT_HOST + '/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    await page.screenshot({ path: `logged-in-${browserType}.png` });
    // Assert logged in OK
    const content = await page.textContent('.card-title')
    assert(content === 'Checklist'); // If we see "Checklist", we're logged in to admin

    // Go to My Subscribers page
    // Crude wait before we check subscribers to allow webhooks time
    await new Promise(x => setTimeout(x, 60000)); //1 minute
    await page.goto(PLAYWRIGHT_HOST + '/admin/subscribers')
    await page.screenshot({ path: `view-subscribers-${browserType}.png` });

    // Click Refresh Subscription
    await page.click('#refresh_subscriptions'); // this is the refresh subscription
    await page.textContent('.alert-heading') === "Notification";
    // screeshot to the active subscriber
    await page.goto(PLAYWRIGHT_HOST + 'admin/dashboard');
    await page.screenshot({ path: `active-subscribers-${browserType}.png` });
    // go back to subscriptions
    await page.goto(PLAYWRIGHT_HOST + '/admin/subscribers')
    // Verify that subscriber is present in the list
    const subscriber_email_content = await page.textContent('.subscriber-email');
    assert(subscriber_email_content === 'john@example.com');

    // Verify that plan is attached to subscriber
    const subscriber_plan_title_content = await page.textContent('.subscription-title');
    assert(subscriber_plan_title_content === 'One-Off Soaps');
   
    // Logout of shop owners admin dashboard
    await page.goto(PLAYWRIGHT_HOST + '/auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    assert(logged_out_content === "You have logged out");
 
    await browser.close();
  }
};

module.exports = test_order_plan_with_only_upfront_charge;

