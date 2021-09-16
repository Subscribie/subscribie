
const { test, expect } = require('@playwright/test');
//Subscribie tests
test("463_show-owner_adding_VAT", async ({ page }) => {
    console.log("enabling VAT...");
     // Go to style your shop
    await page.goto('/admin/vat-settings');
    const style_shop = await page.content("text=VAT Settings");
    expect(style_shop === "VAT Settings");
     //creating category
    console.log("creating category");
    await page.click('text="Yes. Charge VAT at 20%"');
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('adding-VAT.png');
    await page.click('text="Save"');
    await page.textContent('.alert-heading') === "Notification";

});
