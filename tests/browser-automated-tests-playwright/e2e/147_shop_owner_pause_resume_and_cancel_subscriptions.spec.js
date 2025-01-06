const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const SUBSCRIBER_EMAIL_USER = process.env.TEST_SUBSCRIBER_EMAIL_USER;
//Subscribie tests
test.describe("Pause, Resume and Cancel Subscription:", () => {
    test("@147@shop_owner @147_shop_owner_pause_resume_and_cancel_subscriptions", async ({ page }) => {
        await set_test_name_cookie(page, "@147_shop_owner_pause_resume_and_cancel_subscriptions")
        await admin_login(page);
        console.log("Pause and Resume transaction");
        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 1000)); // 5 secconds
        await page.goto('admin/subscribers')

        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === SUBSCRIBER_EMAIL_USER);

        const subscriber_subscription_title_content = await page.textContent('.subscription-title');
        expect(subscriber_subscription_title_content === 'Hair Gel');

        // Verify if subscription active & click cancel 
        const subscription_status = await page.textContent('.subscription-status');
        expect(subscription_status === "active");

        //Pause Subscription
        await page.click('.pause-action');
        await new Promise(x => setTimeout(x, 3000)); // 3 seconds
        await page.click('.pause-yes');
        await new Promise(x => setTimeout(x, 3000)); // 3 seconds
        const subscription_pause_notification = await page.textContent('text="Subscription paused"');
        expect(subscription_pause_notification === "Subscription paused");

        // Click Refresh Subscription
        await page.click('#refresh_subscriptions'); // this is the refresh subscription
        await page.textContent('.alert-heading') === "Notification";
        
        await new Promise(x => setTimeout(x, 3000)); // 3 secconds
        await page.goto('admin/subscribers')

        //Resume Subscription
        await page.click('.resume-action');
        await new Promise(x => setTimeout(x, 3000)); // 3 seconds
        await page.click('.resume-yes');
        await new Promise(x => setTimeout(x, 3000)); // 3 seconds
        const subscription_resume_notification = await page.textContent('text="Subscription resumed"');
        expect(subscription_resume_notification === "Subscription resumed");

        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 1000));
        await page.goto('admin/subscribers');

        // Verify if subscription active & click cancel 
        const subscription_status_resumed = await page.textContent('.subscription-status');
        expect(subscription_status_resumed === "active");

        //Cancel Subscription
        await page.click('.cancel-action');
        await new Promise(x => setTimeout(x, 3000)); // 3 secconds

        await page.click('.cancel-yes');
        await new Promise(x => setTimeout(x, 3000)); // 3 seconds

        const subscription_canceled_notification = await page.textContent('text="Subscription cancelled"');
        expect(subscription_canceled_notification === "Subscription cancelled");
    });
});
