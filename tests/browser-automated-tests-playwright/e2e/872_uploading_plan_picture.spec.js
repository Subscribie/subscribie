const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

test("@872 @872_uploading_plan_picture", async ({ page }) => {
    await admin_login(page);
    await set_test_name_cookie(page, "@872_uploading_plan_picture");

    //uploading an image in a plan
    console.log("Uploading a plan picture");
    await page.goto("/admin/edit")
    const edit_plans_header = await page.textContent('text="Edit Plans"');
    expect(edit_plans_header === "Edit Plans");

    await page.click("text=Hair Gel");
    page.click('[data-file-upload-name="Hair Gel"]');
    console.log("file upload clicked");
    page.on('filechooser', async (fileChooser) => {
        await fileChooser.setFiles('logo-subscribie.png');
    });
    await new Promise(x => setTimeout(x, 3000));
    console.log("saving plan");
    await page.click("text=Save");

    //upload a logo
    await page.goto("/admin/upload-logo")
    console.log("going to the logo upload page")
    const upload_logo_header = await page.textContent('text="Upload logo"');
    expect(upload_logo_header === "Edit Plans");

    page.click('#logo');
    console.log("file upload clicked");
    page.on('filechooser', async (fileChooser) => {
        await fileChooser.setFiles('logo-subscribie.png');
    });
    await new Promise(x => setTimeout(x, 3000));
    console.log("saving logo");
    await page.click("text=Save");

    //verify logo
    await page.goto('/');
    await page.content('input[style="src: cdn/logo-subscribie*; id:logo"]');
    await page.content('input[style="src: cdn/logo-subscribie*; class:plan-img"]');

});
