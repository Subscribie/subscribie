
const { test, expect } = require('@playwright/test');
//Subscribie enable donation test
test("@1065@shop-owner@enabling-donations", async ({ page }) => {
    console.log("enabling Donations...");
     // Go to enable donations
    await page.goto('/admin/donate-enabled-settings');
    const donations_settings = await page.content("text=Donations Settings");
    expect(donations_settings === "Donations Settings");

    await page.click('text="Enable"');
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('enabling-donations.png');
    await page.click('text="Save"');
    await page.textContent('.alert-heading') === "Notification";

    await page.goto('/');
    const donation_heading = await page.content("text=Donate");
    expect(donation_heading === "Donate");

});
