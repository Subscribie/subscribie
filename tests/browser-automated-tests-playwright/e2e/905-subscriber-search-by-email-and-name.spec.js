const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;

test("@905 @905-subscriber-search-by-email-and-name", async ({ page }) => {
  console.log("subscriber filter by name and by email");

  await set_test_name_cookie(page, "@905-subscriber-search-by-email-and-name")
  await admin_login(page);
  await page.goto('admin/subscribers')
  // Verify that subscriber is present in the list
  const mysubscriber_email_content = await page.textContent('.subscriber-email');
  expect(mysubscriber_email_content === SUBSCRIBER_EMAIL_USER);

  // Verify subscriber is linked to the subscribers page:
  const mysubscriber_subscriber_content = await page.textContent('text=John Smith');
  expect(mysubscriber_subscriber_content === 'John smith');

  // Verify search by Name 
  await page.fill('input[name=subscriber_name]', "John");
  await page.click('input[type=submit]');
  expect(mysubscriber_subscriber_content === 'John smith');

  // Verify search by email  
  await page.fill('input[name=subscriber_name]', "");
  await page.fill('input[name=subscriber_email]', SUBSCRIBER_EMAIL_USER);
  await page.click('input[type=submit]');
  expect(mysubscriber_subscriber_content === SUBSCRIBER_EMAIL_USER);

  // Verify search by Name & Email
  await page.fill('input[name=subscriber_name]', "John");
  await page.fill('input[name=subscriber_email]', SUBSCRIBER_EMAIL_USER);
  await page.click('input[type=submit]');
  expect(mysubscriber_subscriber_content === 'John smith');
});

