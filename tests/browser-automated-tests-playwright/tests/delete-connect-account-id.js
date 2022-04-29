const { test, expect } = require('@playwright/test');
// Clear connect account id after all tests are completed
test("@831@delete-connect-account-id", async ({ page }) => {

    await page.goto('/admin/delete-connect-account');
    await new Promise(x => setTimeout(x, 2000)); //2 secconds
    await page.goto('admin/dashboard')
    const connect_to_stripe = await page.textContent('text="Review Stripe"');
    expect (connect_to_stripe == 'Review Stripe');


}); 
