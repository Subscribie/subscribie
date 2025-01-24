const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

test("@334-shop-owner-create-private-page", async ({ page }) => {
  // Login
  await admin_login(page);
  await set_test_name_cookie(page, "@334-shop-owner-create-private-page");

  console.log("Creating Private page creation");
  await page.goto('/pages/add-page');
  await page.fill("input[name='page-title']", 'Private Test Page');
  await page.fill("div[role='textbox']", 'This is a Private Page');
  await page.click('text="Save"');

  await page.goto('/pages/private-pages');
  await page.content("text='Update Private Pages'");
  await page.getByLabel("Private Test Page").first().click()
  for (const li of await page.getByLabel("Private Test Page").all())
    await li.click();

  await page.click("text='Submit'");

  await page.goto('/page/privatetestpage');
  await page.textContent("text='This is a Private Page'");
  console.log("Private Page succeeded");

  console.log("Logging out to check for the private page");
  await page.goto('/auth/logout');
  await page.content("text='You have logged out'");
  console.log("Logged out");

  await page.goto('/page/privatetestpage');
  let private_page_content = await page.evaluate(() => document.body.textContent);
  if (private_page_content.indexOf("This is a Private Page") > -1) {
    console.log("ERROR: the page is not private")
    return 1
  }
  else {
    console.log("Private Page not available for the public.(Succeeded)");
  }
});
