
const { test, expect } = require('@playwright/test');
//Subscribie tests
test("@1005@shop_owner@terms and condition creation", async ({ page }) => {
  try{
    console.log("checking if terms and conditions is already attached to the free plan...");
    await page.goto('/');
    await page.click('[name="Free plan"]');
    page.setDefaultTimeout(3000);
    await new Promise(x => setTimeout(x, 1000));
    let terms_and_conditions_attached = await page.evaluate(() => document.body.textContent);
    if (terms_and_conditions_attached.indexOf("Terms and Conditions") > -1) {
        await new Promise(x => setTimeout(x, 1000));
        await page.click('text="Terms and Conditions"');
        await page.locator('text=testing');
        console.log("terms and conditions is already attached to the free plan");
        return 0
        }
      } catch (e) {
        console.log("Continuing with creating the terms and conditions");
      }
     // Go to add documents
    await page.goto('/admin/list-documents');
    await page.click('text="Add Document"');
     //creating terms and conditions document
    console.log("creating terms and conditions document");
    await page.fill("input[name='document']", 'Terms and Conditions');
    await page.fill(".note-editable", 'testing');
    await page.click('text="Save"');
    console.log("terms and conditions saved");

    const terms_and_conditions_created = await page.content("#alert-heading");
    expect(terms_and_conditions_created === "added new document: Terms and Conditions");
      // adding terms and conditions to free plan
    console.log("attaching terms and conditions to free plan");
    await page.click("[name='Terms and Conditions-document']");
    const category_plans = await page.textContent("text=Document - Assign Plan");
    expect(category_plans === "Document - Assign Plan");

    await page.click("text=Free plan");
    await new Promise(x => setTimeout(x, 1000));
    await page.click('text="Save"');

    const free_plan_added = await page.content("#alert-heading");
    expect(free_plan_added === "Notification");

      // checking if terms and condition is attached to the free plan. 
    await page.goto('/');
    await page.click('[name="Free plan"]');
    const terms_and_conditions_attached = await page.textContent("text=Terms and Conditions")
    expect(terms_and_conditions_attached === "Terms and Conditions");
    console.log("terms and conditions is attached to the free plan");
    expect(await page.screenshot()).toMatchSnapshot('terms-conditions-in-shop-owner-side.png');
    await new Promise(x => setTimeout(x, 1000));

    // checking if terms and condition can be seen
    await page.click('text="Terms and Conditions"');
    await page.locator('text=testing');

});
