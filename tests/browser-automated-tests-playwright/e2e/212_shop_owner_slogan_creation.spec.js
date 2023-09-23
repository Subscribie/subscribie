const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

//Subscribie tests
test("@212@shop-owner@slogan creation @212_shop_owner_slogan_creation", async ({ page }) => {
  await admin_login(page);
  await set_test_name_cookie(page, "@212_shop_owner_slogan_creation");
  console.log("checking if slogan is already created...");
  await page.goto('/');
  let slogan_exists = await page.evaluate(() => document.body.textContent);
  if (slogan_exists === 'this is a slogan') {
    console.log("slogan already created, exiting test");
    test.skip();
  }
  // Go to edit plan page
  await page.goto('/admin/edit');

  //edit slogan
  await page.fill("input[name='slogan']", 'this is a slogan');
  await page.click("text=Hair Gel");
  await page.click('text="Save"');

  //verify home page plan creation
  await page.goto("/");
  await new Promise(x => setTimeout(x, 1000)); // 1 secconds
  const slogan_created = await page.textContent('text=this is a slogan');
  expect(slogan_created === 'this is a slogan');
  // TODO screenshot cooling off plan 
});