const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const SUBSCRIBER_EMAIL_USER = process.env.TEST_SUBSCRIBER_EMAIL_USER;

test.describe("order free plan tests:", () => {
    test("@939 @subscriber @939_subscriber_order_free_plan_with_terms_and_conditions", async ({ page }) => {
        console.log("Ordering free plan...");
        await set_test_name_cookie(page, "@939_subscriber_order_free_plan_with_terms_and_conditions");
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
        await page.click('text="Continue to Payment"');

        // Verify get to the thank you page order complete
        const order_complete_content = await page.textContent('.title-1');
        expect(order_complete_content === "Order Complete!");

        // admin login
        await admin_login(page);
        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await page.goto('/admin/subscribers')

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
