
const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');



//Subscribie tests
test("@452@shop-owner@category creation @452_shop_owner_create_category", async ({ page }) => {

  // Login
  await admin_login(page);
  await set_test_name_cookie(page, "@452@shop-owner@category creation")
  // Go to add category
  await page.goto('/admin/add-category');

  //creating category
  console.log("creating category");
  await page.fill("input[name='category']", 'basic plan');
  await page.click('text="Save"');

  const category_created = await page.content("#alert-heading");
  expect(category_created === "Notification");
  // adding plans to category
  console.log("adding plans to category");
  await page.click("[name='basic plan-category']");
  const category_plans = await page.textContent("text=Category - Assign Plan");
  expect(category_plans === "Category - Assign Plan");

  await page.click("text=Hair Gel");
  await new Promise(x => setTimeout(x, 1000));
  await page.click("text=Bath Soaps");
  await new Promise(x => setTimeout(x, 1000));
  await page.click("text=One-Off Soaps");
  await new Promise(x => setTimeout(x, 1000));

  await page.click('text="Save"');

  const plans_added = await page.content("#alert-heading");
  expect(plans_added === "Notification");

  // checking if category was created. 
  await page.goto('/');
  const category_added = await page.content("text=basic plan");
  expect(category_added === "basic plan");
  console.log("the category created");
});