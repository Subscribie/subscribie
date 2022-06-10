const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;

test.describe("order plan with only upfront charge tests:", () => {
    test("@293@subscriber@Ordering upfront plan", async ({ page }) => {
        console.log("Ordering plan with only upfront charge...");
        // Buy item with subscription & upfront fee
        await page.goto('/'); // Go to home before selecting product
        await page.click('[name="One-Off Soaps"]');

        // Fill in order form
        await page.fill('#given_name', 'John');
        await page.fill('#family_name', 'Smith');
        await page.fill('#email', SUBSCRIBER_EMAIL_USER);
        await page.fill('#mobile', '07123456789');
        await page.fill('#address_line_one', '123 Short Road');
        await page.fill('#city', 'London');
        await page.fill('#postcode', 'L01 T3U');
        expect(await page.screenshot()).toMatchSnapshot('upfront-new-customer-form.png');
        await page.click('text="Continue to Payment"');

        // Begin stripe checkout
        const order_summary_content = await page.textContent(".title-1");
        expect(order_summary_content === "Order Summary");
        expect(await page.screenshot()).toMatchSnapshot('upfront-pre-stripe-checkout.png');
        await page.click('#checkout-button');

        //Verify first payment is correct (upfront charge + first recuring charge)
        const first_payment_content = await page.textContent('#ProductSummary-totalAmount');
        expect(first_payment_content === "£5.66");
        const upfront_charge_content = await page.textContent('.Text-fontSize--16');
        expect(upfront_charge_content === "One-Off Soaps");

        // Pay with test card
        await page.fill('#cardNumber', '4242 4242 4242 4242');
        await page.fill('#cardExpiry', '04 / 24');
        await page.fill('#cardCvc', '123');
        await page.fill('#billingName', 'John Smith');
        await page.selectOption('select#billingCountry', 'GB');
        await page.fill('#billingPostalCode', 'LN1 7FH');
        expect(await page.screenshot()).toMatchSnapshot('upfront-stripe-checkout-filled.png');
        await page.click('.SubmitButton');
    
        // Verify get to the thank you page order complete
        const order_complete_content = await page.textContent('.title-1');
        expect(order_complete_content === "Order Complete!");
        expect(await page.screenshot()).toMatchSnapshot('upfront-order-complete.png');

        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 5000)); //5 seconds
        await page.goto('/admin/subscribers')
        expect(await page.screenshot()).toMatchSnapshot('upfront-view-subscribers.png');

        // Click Refresh Subscription
        await page.click('#refresh_subscriptions'); // this is the refresh subscription
        await page.textContent('.alert-heading') === "Notification";
        // screeshot to the active subscriber
        await page.goto('admin/dashboard');
        expect(await page.screenshot()).toMatchSnapshot('upfront-active-subscribers.png');
        // go back to subscriptions
        await page.goto('/admin/subscribers')
        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === SUBSCRIBER_EMAIL_USER);

        // Verify that plan is attached to subscriber
        const subscriber_plan_title_content = await page.textContent('.subscription-title');
        expect(subscriber_plan_title_content === 'One-Off Soaps');
    });
});
