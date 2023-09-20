const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;

test.describe("order free plan tests:", () => {
    test("@1219 @shop-owner @enable custom url", async ({ page }) => {

        await page.goto('/admin/change-thank-you-url');
        await page.fill('#url', 'google.com');
        await page.click('role=button[name="Save"]');
        await new Promise(x => setTimeout(x, 2000));
        const custom_url = await page.textContent('text="custom url changed to https://google.com"');
        expect(custom_url  === 'custom url changed to https://google.com');

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
        await expect(page.getByRole('img', { name: 'Google' })).toBeVisible();
        expect(await page.screenshot()).toMatchSnapshot('custom-page-redirect.png');

        //changing it back to the default 
        await page.goto('/admin/change-thank-you-url');
        await page.fill('#url', 'default');
        await page.click('role=button[name="Save"]');
        await new Promise(x => setTimeout(x, 2000));
        const default_custom_url = await page.textContent('text="custom url changed to https://default"');
        expect(default_custom_url === 'custom url changed to https://default');
    });
});
