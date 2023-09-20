const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;

test.describe("order free plan tests:", () => {
    test("@1219 @shop-owner @enable custom url @1219_shop-owner_enable_custom_url", async ({ page }) => {

        await admin_login(page);
        await page.goto('/admin/change-thank-you-url');
        await page.fill('#url', 'google.com');
        await page.click('role=button[name="Save"]');
        await new Promise(x => setTimeout(x, 2000));
        const custom_url = await page.textContent('text="custom url changed to https://google.com"');
        expect(custom_url  === 'custom url changed to https://google.com');

        console.log("Ordering plan with only recurring charge...");
        // Buy item with subscription & upfront fee
        await page.goto("/"); // Go to home before selecting product
        await page.click('[name="Bath Soaps"]');

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
        expect(payment_content === "£10.99");
        const recuring_charge_content = await page.textContent('.Text-fontSize--16');
        expect(recuring_charge_content === "Subscribe to Bath Soaps");

        // Pay with test card
        await page.fill('#cardNumber', '4242 4242 4242 4242');
        await page.fill('#cardExpiry', '04 / 24');
        await page.fill('#cardCvc', '123');
        await page.fill('#billingName', 'John Smith');
        await page.selectOption('select#billingCountry', 'GB');
        await page.fill('#billingPostalCode', 'LN1 7FH');
        await page.click('.SubmitButton');

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
