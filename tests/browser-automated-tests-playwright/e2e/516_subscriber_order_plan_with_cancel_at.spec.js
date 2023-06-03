const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const { fetch_upcomming_invoices } = require('./features/fetch_upcomming_invoices')

const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;
test.describe("order plan with cancel at:", () => {
  test("@516 @516_shop_owner_order_plan_with_cancel_at", async ({ page }) => {
    await admin_login(page);
    await set_test_name_cookie(page, "@516_shop_owner_order_plan_with_cancel_at")
    console.log("Ordering plan with cancel_at");
    // Go to home before selecting product
    await page.goto('/');
    // Choosing plan with cancel at 
    await page.click('[name="cancel at plan"]');

    // Fill in order form
    await page.fill('#given_name', 'John');
    await page.fill('#family_name', 'Smith');
    await page.fill('#email', SUBSCRIBER_EMAIL_USER);
    await page.fill('#mobile', '07123456789');
    await page.fill('#address_line_one', '123 Short Road');
    await page.fill('#city', 'London');
    await page.fill('#postcode', 'L01 T3U');
    await page.click('.btn-primary-lg');
    // Begin stripe checkout
    const order_summary_content = await page.textContent(".title-1");
    expect(order_summary_content === "Order Summary");
    await page.click('#checkout-button');

    //Verify first payment is correct (recuring charge only)
    const payment_content = await page.textContent('div.mr2.flex-item.width-fixed');
    expect(payment_content === "£10.00");
    const recuring_charge_content = await page.textContent('.Text-fontSize--16');
    expect(recuring_charge_content === "Subscribe to cancel at plan");

    // Pay with test card
    await page.fill('#cardNumber', '4242 4242 4242 4242');
    await page.fill('#cardExpiry', '04 / 24');
    await page.fill('#cardCvc', '123');
    await page.fill('#billingName', 'John Smith');
    await page.selectOption('select#billingCountry', 'GB');
    await page.fill('#billingPostalCode', 'LN1 7FH');
    await page.click('.SubmitButton');

    // Verify get to the thank you page order complete
    const order_complete_content = await page.textContent('.title-1');
    expect(order_complete_content === "Order Complete!");

    // Go to My Subscribers page
    // Crude wait before we check subscribers to allow webhooks time
    await new Promise(x => setTimeout(x, 5000)); //5 secconds
    await page.goto('/admin/subscribers')

    // Click Refresh Subscription
    await page.click('#refresh_subscriptions'); // this is the refresh subscription
    await page.textContent('.alert-heading') === "Notification";

    // TODO screenshot to the trialing subscriber
    await page.goto('admin/dashboard');
    // go back to subscriptions
    await page.goto('/admin/subscribers')

    // Verify that subscriber is present in the list
    const subscriber_email_content = await page.textContent('.subscriber-email');
    expect(subscriber_email_content === SUBSCRIBER_EMAIL_USER);

    // Verify that plan is attached to subscriber
    const subscriber_plan_title_content = await page.textContent('.subscription-title');
    expect(subscriber_plan_title_content === 'cancel at plan');

    const content_subscriber_plan_interval_amount = await page.textContent('.subscribers-plan-interval_amount');
    expect(content_subscriber_plan_interval_amount === '£10.00');

    const subscriber_plan_sell_price_content = await page.evaluate(() => document.querySelector('.subscribers-plan-sell-price').textContent.indexOf("(No up-front fee)"));
    expect(subscriber_plan_sell_price_content > -1)

    const subscriber_plan_cancel_at_content = await page.textContent('text="Automatically Cancels at:"');
    expect(subscriber_plan_cancel_at_content === "Automatically Cancels at:");


    // Go to upcoming payments and ensure plan is attached to upcoming invoice
    await page.goto('/admin/upcoming-invoices');
    // Fetch Upcoming Invoices
    await fetch_upcomming_invoices(page);
    const content_upcoming_invoice_plan_price_interval = await page.textContent('.plan-price-interval');
    expect(content_upcoming_invoice_plan_price_interval === '£10.00');

    const content_upcoming_invoice_plan_sell_price = await page.textContent('.upcoming-invoices-plan-no-sell_price');
    expect(content_upcoming_invoice_plan_sell_price === '(No up-front cost)');

    const subscriber_plan_title_upcoming_payment = await page.textContent('text="cancel at plan"');
    expect(subscriber_plan_title_upcoming_payment === "Plan: cancel at plan");
  });
});
