const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;

test.describe("order free plan tests:", () => {
    test("@939 @subscriber @Ordering free plan @GBP", async ({ page }) => {
        console.log("Ordering free plan...");
        // Buy item with subscription & upfront fee
        await page.goto('/'); // Go to home before selecting product
        await page.click('[name="Free plan"]');

        // Fill in order form
        await page.fill('#given_name', 'John');
        await page.fill('#family_name', 'Smith');
        await page.fill('#email', SUBSCRIBER_EMAIL_USER);
        await page.fill('#mobile', '07123456789');
        await page.fill('#address_line_one', '123 Short Road');
        await page.fill('#city', 'London');
        await page.fill('#postcode', 'L01 T3U');
        expect(await page.screenshot()).toMatchSnapshot('freeplan-new-customer-form.png');
        await page.click('text="Continue to Payment"');

        // Verify get to the thank you page order complete
        const order_complete_content = await page.textContent('.title-1');
        expect(order_complete_content === "Order Complete!");
        expect(await page.screenshot()).toMatchSnapshot('freeplan-order-complete.png');

        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await page.goto('/admin/subscribers')
        expect(await page.screenshot()).toMatchSnapshot('freeplan-view-subscribers.png');

        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === SUBSCRIBER_EMAIL_USER);

        // Verify that plan is attached to subscriber
        const subscriber_plan_title_content = await page.textContent('.subscription-title');
        expect(subscriber_plan_title_content === 'Free plan');

        // Verify that plan is attached with terms and conditions
        const subscriber_plan_terms_and_conditions = await page.textContent('text="Terms and Conditions"');
        expect(subscriber_plan_terms_and_conditions === 'Terms and conditions');

        // Verify that as a shop owner i can see the terms and conditions attached
        await page.click('text="Terms and Conditions"');
        const subscriber_terms_and_conditions = await page.textContent('text="testing"');
        expect(subscriber_terms_and_conditions === "testing");

        // Verify that as a shop owner i can see the terms and conditions attached
        await page.goto('/admin/list-documents');
        await page.click('text=Show agreed');
        const subscriber_agreed_terms_and_conditions = await page.textContent('text="terms-and-conditions-agreed"');
        expect(subscriber_agreed_terms_and_conditions === 'terms-and-conditions-agreed');
        
        // Verify the termns and conditions can be seen in the subscriber view
        await page.click('text="Subscriber: John"');
        page.locator('text=Subscriber: John');
        page.locator('text=Terms and Conditions');

        await page.click('text="Terms and Conditions"');
        await page.locator('text=testing');
        
    });
});
