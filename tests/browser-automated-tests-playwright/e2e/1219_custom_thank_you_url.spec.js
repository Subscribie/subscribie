const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;
const { admin_login } = require('./features/admin_login');
test.describe("order free plan tests:", () => {
    test("@1219 @shop-owner @1219_custom_thank_you_url @1219_shop-owner_enable_custom_url", async ({ page }) => {

        await admin_login(page);
        await page.goto('/admin/change-thank-you-url');
        await page.fill('#custom_thank_you_url', 'https://www.google.com');
        await page.click('role=button[name="Save"]');
        const custom_url = await page.textContent('text="Custom thank you url changed to: https://www.google.com"');
        expect(custom_url  === 'Custom thank you url changed to: https://www.google.com');

        console.log("Ordering plan with only recurring charge...");
        // Buy item with subscription & upfront fee
        await page.goto("/"); // Go to home before selecting product
        await page.click('[name="Free plan"]');

        // Fill in order form
        await page.fill('#given_name', 'John');
        await page.fill('#family_name', 'Smith');
        await page.fill('#email', SUBSCRIBER_EMAIL_USER);
        await page.fill('#mobile', '07123456789');
        await page.fill('#address_line_one', '123 Short Road');
        await page.fill('#city', 'London');
        await page.fill('#postcode', 'L01 T3U');
        await page.click('.btn-primary-lg');

        // Verify get to the thank you page order complete
        await page.waitForURL('https://www.google.com');
        //changing it back to the default 
        await page.goto('/admin/change-thank-you-url');
        await page.getByRole('button', { name: 'default'}).click();
        await new Promise(x => setTimeout(x, 2000));
        await expect(page.getByText('Notification Thank page has')).toContainText("Thank page has been set back to the to the default thank you page");
    });
});
