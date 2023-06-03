
const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');


test("@463@shop-owner@adding VAT @463_shop_owner_adding_vat", async ({ page }) => {
    await admin_login(page);
    await set_test_name_cookie(page, "@463_shop_owner_adding_vat");
    console.log("enabling VAT...");
    // Go to style your shop
    await page.goto('/admin/vat-settings');
    const VAT_settings = await page.content("text=VAT Settings");
    expect(VAT_settings === "VAT Settings");

    await page.click('text="Yes. Charge VAT at 20%"');
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('adding-VAT.png');
    await page.click('text="Save"');
    await page.textContent('.alert-heading') === "Notification";

});
