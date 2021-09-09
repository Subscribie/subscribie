const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe("Pause, Resume and Cancel Subscription:", () => {
    test("147_shop-owner_Pause and Resume transaction", async ({ page }) => {  
        console.log("Pause and Resume transaction");      
        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 1000)); // 5 secconds
        await page.goto('admin/subscribers')

        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === 'john@example.com');

        const subscriber_subscription_title_content = await page.textContent('.subscription-title');
        expect(subscriber_subscription_title_content === 'Hair Gel');
        
        // Verify if subscription active & click cancel 
        const subscription_status = await page.textContent('.subscription-status');
        expect(subscription_status === "active");
        
        //Pause Subscription
        await page.click('.pause-action');
        const subscription_pause_notification = await page.textContent('text="Subscription paused"');
        expect(subscription_pause_notification === "Subscription paused");
        expect(await page.screenshot()).toMatchSnapshot('paused-plan.png');

        await new Promise(x => setTimeout(x, 3000)); // 3 secconds
        
        //Resume Subscription
        await page.click('.resume-action');
        const subscription_resume_notification = await page.textContent('text="Subscription resumed"');
        expect(subscription_resume_notification === "Subscription resumed");
        expect(await page.screenshot()).toMatchSnapshot('resume-plan.png');

    });
    test("Cancel transaction", async ({ page }) => {
        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 1000)); // 5 secconds
        await page.goto('admin/subscribers');

        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === 'john@example.com');

        const subscriber_subscription_title_content = await page.textContent('.subscription-title');
        expect(subscriber_subscription_title_content === 'Hair Gel');
        
        // Verify if subscription active & click cancel 
        const subscription_status = await page.textContent('.subscription-status');
        expect(subscription_status === "active");

        //Cancel Subscription
        await page.click('.cancel-action');
        await new Promise(x => setTimeout(x, 3000)); // 3 secconds

        await page.click('.cancel-yes');
        await new Promise(x => setTimeout(x, 3000)); // 3 seconds

        subscription_canceled_notification = await page.textContent('text="Subscription cancelled"');
        expect(subscription_canceled_notification === "Subscription cancelled");
        expect(await page.screenshot()).toMatchSnapshot('cancel-plan.png');

    });
});
