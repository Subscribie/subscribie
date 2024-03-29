const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const { test, expect } = require('@playwright/test');
//Subscribie enable donation test
test("@1065 @1065_shop_owner_enabling_donations", async ({ page }) => {
    console.log("enabling Donations...");
    await admin_login(page);
    await set_test_name_cookie(page, "@1065_shop_owner_enabling_donations");
    // Go to enable donations
    await page.goto('/admin/donate-enabled-settings');
    const donations_settings = await page.content("text=Donations Settings");
    expect(donations_settings === "Donations Settings");

    await page.click('text="Enable"');
    await page.click('text="Save"');
    await page.textContent('.alert-heading') === "Notification";

    //Check the admin dashboard if donors settings are enabled in the dashboard
    await page.goto('/admin/dashboard');
    const donations_in_dashboard = await page.content("text=Donations to your shop");
    expect(donations_in_dashboard === "Donations to your shop");

    await page.goto('/');
    const donation_heading = await page.content("text=Donate");
    expect(donation_heading === "Donate");
});
