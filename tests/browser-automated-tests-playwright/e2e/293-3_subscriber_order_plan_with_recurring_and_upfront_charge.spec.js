const { test, expect } = require('@playwright/test');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const { admin_login } = require('./features/admin_login');
const { fetch_upcomming_invoices } = require('./features/fetch_upcomming_invoices');

const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;
test.describe("order plan with recurring and upfront charge test:", () => {
    test("@293-3 @293-3_subscriber_order_plan_with_recurring_and_upfront_charge", async ({ page }) => {
        console.log("@293-3_subscriber_order_plan_with_recurring_and_upfront_charge");
        await set_test_name_cookie(page, "@293-3_subscriber_order_plan_with_recurring_and_upfront_charge")
        // Buy item with subscription & upfront fee
        await page.goto('/'); // Go to home before selecting product
        await page.click('[name="Hair Gel"]');

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

        //Verify first payment is correct (upfront charge + first recuring charge)
        const first_payment_content = await page.textContent('#ProductSummary-totalAmount');
        expect(first_payment_content === "£5.99");
        const recuring_charge_content = await page.textContent('#ProductSummary-description');
        expect(recuring_charge_content === "Then £5.99 per week");

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

        await admin_login(page);
        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 5000)); //5 secconds
        await page.goto('admin/subscribers')

        // Click Refresh Subscription
        await page.click('#refresh_subscriptions'); // this is the refresh subscription
        await page.textContent('.alert-heading') === "Notification";
        // screeshot to the active subscriber
        await page.goto('admin/dashboard');
        //go back to subscriptions
        await page.goto('admin/subscribers')

        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === SUBSCRIBER_EMAIL_USER);

        // Verify that plan is attached to subscriber
        const subscriber_subscription_title_content = await page.textContent('.subscription-title');
        expect(subscriber_subscription_title_content === 'Hair Gel');

        // Verify transaction is present in 'All transactions page'
        await page.goto('admin/transactions')
        const transaction_content = await page.textContent('.transaction-amount');
        expect(transaction_content == '£5.99');

        // Verify subscriber is linked to the transaction:
        const transaction_subscriber_content = await page.textContent('.transaction-subscriber');
        expect(transaction_subscriber_content === 'John smith');

        // Verify paid invoice has been generated & marked "paid":
        await page.goto('admin/invoices')
        const content_paid_invoice_status = await page.textContent('.invoice-status');
        expect(content_paid_invoice_status === 'paid')

        const content_paid_invoice_amount = await page.textContent('.invoice-amount-paid');
        expect(content_paid_invoice_amount === '£5.99')

        // Verify upcoming invoice has been generated for the subscription:
        await page.goto('admin/upcoming-invoices')
        // Fetch Upcoming Invoices
        await fetch_upcomming_invoices(page);
        const content_upcoming_invoice_amount = await page.textContent('.upcoming-invoice-amount');
        expect(content_upcoming_invoice_amount === '£5.99')

        // Verify Plan is attached to upcoming invoice, and recuring price & upfront price are correct
        const content_upcoming_invoice_plan_recuring_amount = await page.textContent('.plan-price-interval');
        expect(content_upcoming_invoice_plan_recuring_amount === '£5.99')
        const content_upcoming_invoice_plan_upfront_amount = await page.textContent('.plan-sell-price');
        expect(content_upcoming_invoice_plan_upfront_amount === '£1.00')
    });
});
