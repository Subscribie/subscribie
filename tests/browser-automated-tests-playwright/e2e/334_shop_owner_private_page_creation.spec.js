const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

test("@334@shop-owner@Creating Private Page @334-shop-owner-create-private-page", async ({ page }) => {
  // Login
  await admin_login(page);
  await set_test_name_cookie(page, "@334-shop-owner-create-private-page");
  await page.goto('/page/privatetestpage');

  console.log("Continuing with Private page creation");
  await page.goto('/pages/add-page');
  await page.fill("input[name='page-title']", 'Private Test Page');
  await page.fill("div[role='textbox']", 'This is a Private Page');
  await page.click('text="Save"');
  const page_created = await page.content("#alert-heading");
  expect(page_created === "Notification");
  console.log("Page already created, now configuring to private");

  await page.goto('/pages/private-pages');
  const private_page_feature = await page.content("text='Update Private Pages'");
  expect(private_page_feature === "Update Private Pages");
  page.click("input[type=checkbox]");
  page.click("text='Submit'");

  const private_page_created = await page.content("#alert-heading");
  expect(private_page_created === "Notification");
  console.log("Private Page created");

  await page.goto('/page/privatetestpage');
  const visiting_private_page = await page.textContent("text='This is a Private Page'");
  expect(visiting_private_page === "This is a Private Page");
  console.log("Private Page succedded");

  console.log("Logging out to check for the private page");
  await page.goto('/auth/logout');
  const log_out = await page.content("text='You have logged out'");
  expect(log_out === "You have logged out");
  console.log("Logged out");

  await page.goto('/page/privatetestpage');
  let private_page_content = await page.evaluate(() => document.body.textContent);
  if (private_page_content.indexOf("This is a Private Page") > -1) {
    console.log("ERROR: the page is not private")
    return 1
  }
  else {
    console.log("Private Page not avaliable for the public.(Succeded)");
  }
});
