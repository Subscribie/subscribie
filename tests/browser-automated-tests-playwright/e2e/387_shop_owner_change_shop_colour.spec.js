
const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

test("@387@shop-owner@change_shop_colour @387_shop_owner_change_shop_colour", async ({ page }) => {
    await admin_login(page);
    await set_test_name_cookie(page, "@387_shop_owner_change_shop_colour");

    console.log("changing shop colour...");
    // Go to style your shop
    await page.goto('/style/style-shop');
    const style_shop = await page.content("text=Style Your Shop");
    expect(style_shop === "Style Your Shop");

    await page.fill('input[name="primary"]', "0b5394");
    await new Promise(x => setTimeout(x, 3000));
    await page.fill('input[name="font"]', "000000");
    await page.click('text="Save"');
    expect(await page.screenshot()).toMatchSnapshot('changing-shop-colour.png');

    // check if its changed
    console.log("checking if shop style has changed");
    await page.goto('/style/style-shop');
    await page.content('input[style="background-color: rgb(11, 83, 148); color: white;"]');

    //screenshot of the changed style shop;
    await page.goto('/');
    expect(await page.screenshot()).toMatchSnapshot('changed shop color.png');

});
