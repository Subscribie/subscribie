const { test, expect } = require('@playwright/test');

test("@872@shop-owner@uploading a plan picture", async ({ page }) => {
    console.log("Uploading a plan picture");
    await page.goto("/admin/edit")
    const check_plan_with_choice_and_options = await page.textContent('text="Edit Plans"');
    expect(check_plan_with_choice_and_options === "Edit Plans");

    //change order with recurring and upfront
    await page.click("text=Hair Gel");
    page.click('[data-file-upload-name="Hair Gel"]');
    console.log("file upload clicked");
    page.on('filechooser', async (fileChooser) => {
        await fileChooser.setFiles('logo-subscribie.png');
    });
    await new Promise(x => setTimeout(x, 3000));
    console.log("saving plan");
    await page.click("text=Save");

});
