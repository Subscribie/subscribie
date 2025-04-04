const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const { fetch_upcomming_invoices } = require('./features/fetch_upcomming_invoices');

const SUBSCRIBER_EMAIL_USER = process.env.TEST_SUBSCRIBER_EMAIL_USER;
test("@264@subscriber @264_subscriber_order_plan_with_choice_options_and_required_note", async ({ page }) => {
        await admin_login(page);
        await set_test_name_cookie(page, "@264_subscriber_order_plan_with_choice_options_and_required_note")
        console.log("order plan with choice, option and required note");
        // Buy item with subscription & upfront fee
        await page.goto('/'); // Go to home before selecting product
        // Choosing plan with Cooling off period
        await page.click('[name="Plan with choice and options"]');

        // Choose Options
        const choose_option = await page.textContent("text=Choose your options");
        expect(choose_option === "Choose your options");
        await page.getByLabel('Red').first().click();
        await page.click('text=Save');

        // Fill in order form
        await page.fill('#given_name', 'John');
        await page.fill('#family_name', 'Smith');
        await page.fill('#email', SUBSCRIBER_EMAIL_USER);
        await page.fill('#mobile', '07123456789');
        await page.fill('#address_line_one', '123 Short Road');
        await page.fill('#city', 'London');
        await page.fill('#postcode', 'L01 T3U');
        await page.fill("textarea[name='note_to_seller']", "Purple")
        await page.click('.btn-primary-lg');

        // Begin stripe checkout
        const order_summary_content = await page.textContent(".title-1");
        expect(order_summary_content === "Order Summary");
        await page.click('#checkout-button');


        // Pay with test card
        await page.fill('#cardNumber', '4242 4242 4242 4242');
        await page.fill('#cardExpiry', '04 / 30');
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
        expect(subscriber_plan_title_content === 'Plan with choice and options');

        const content_subscriber_plan_interval_amount = await page.locator('css=span.plan-price-interval').filter({ hasTest: '£15' });
        expect(content_subscriber_plan_interval_amount === '£15.00');

        const subscriber_plan_sell_price_content = await page.evaluate(() => document.querySelector('.subscribers-plan-sell-price').textContent.indexOf("(No up-front fee)"));
        expect(subscriber_plan_sell_price_content > -1)

        const subscriber_plan_choice_content = await page.textContent('text="Red"');
        expect(subscriber_plan_choice_content === "Red");

        await page.textContent('text="Purple"');

        // Go to upcoming payments and ensure plan is attached to upcoming invoice
        await page.goto('/admin/upcoming-invoices');
        // Fetch Upcoming Invoices
        await fetch_upcomming_invoices(page);
        await page.reload();
        await page.locator('css=span.plan-price-interval', {hasText: "£15.00"}).first().textContent() === '£15.00';

        const content_upcoming_invoice_plan_sell_price = await page.textContent('.upcoming-invoices-plan-no-sell_price');
        expect(content_upcoming_invoice_plan_sell_price === '(No up-front cost)');
});
