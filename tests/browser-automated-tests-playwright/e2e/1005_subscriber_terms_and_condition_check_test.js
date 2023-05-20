const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;


test('@1005@subscriber@check terms and conditions', async ({ page }) => {

  
  await page.goto("/auth/logout");
  await page.goto("/account/logout");
  //login in as subscriber
  await page.goto("/account/login");
  await page.fill('#email', SUBSCRIBER_EMAIL_USER);
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
  expect(await page.screenshot()).toMatchSnapshot('terms-and-conditions-attached-subscribers.png');
  await new Promise(x => setTimeout(x, 1000));


});
