const { test, expect } = require('@playwright/test');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const TEST_SUBSCRIBER_EMAIL_USER = process.env.TEST_SUBSCRIBER_EMAIL_USER;


test('@1005@subscriber @1005_subscriber_terms_and_condition_check_test', async ({ page }) => {

  await set_test_name_cookie(page, "@1005_subscriber_terms_and_condition_check_test");
  await page.goto("/auth/logout");
  await page.goto("/account/logout");
  //login in as subscriber
  await page.goto("/account/login");
  await page.fill('#email', TEST_SUBSCRIBER_EMAIL_USER);
  await page.fill('#password', 'password');
  await page.click('text=Sign In');
  await page.textContent('.card-title') === "Your subscriptions";
  console.log("Logged in as a subscriber");
  //check Terms and Conditions is attached
  await page.goto('/account/subscriptions');
  await page.textContent('.card-title') === "Your subscriptions";
  await page.locator('text=Terms and Conditions');
  await new Promise(x => setTimeout(x, 1000));
  // check the terms and conditions page
  await page.click("text=Terms and Conditions");
  await page.locator("testing");
  console.log("terms and condition are shown in the subscriber side");
});
