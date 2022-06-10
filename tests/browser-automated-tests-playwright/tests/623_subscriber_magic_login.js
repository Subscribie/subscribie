const { test, expect } = require('@playwright/test');
const checkSubscriberLogin= require('./checkSubscriberLogin.js');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;


test('@623@subscriber@reset password receives email', async ({ page }) => {

  
  await page.goto("/auth/logout");
  await page.goto("/account/forgot-password");
  await page.fill('#email', SUBSCRIBER_EMAIL_USER);
  await page.click("text=Submit");
  await new Promise(r => setTimeout(r, 5000));
  checkSubscriberLogin.checkSubscriberLogin();
  console.log("checking reset password");
  await new Promise(r => setTimeout(r, 5000));
  console.log("the password url is: ");
  console.log(checkSubscriberLogin.reset_password_url);
  await page.goto(checkSubscriberLogin.reset_password_url);
  await new Promise(r => setTimeout(r, 5000));
  //reseting password
  console.log("reseting password");
  const order_summary_content = await page.textContent("text=Set a new password");
  expect(order_summary_content === "Set a new password");
  //changing password
  await page.fill('#password', 'password');
  await page.click("text=Submit");
  await page.textContent('.alert-heading') === "Notification";
  console.log("password changed");
  //login in as subscriber
  await page.goto("/account/login");
  await page.fill('#email', SUBSCRIBER_EMAIL_USER);
  await page.fill('#password', 'password');
  await page.click('text=Sign In');
  await page.textContent('.card-title') === "Your subscriptions";
  console.log("Logged in as a subscriber");
  //check subscriptions
  await page.goto("/account/subscriptions");
  await page.textContent('text=Subscriptions') === "Subscriptions";
  await page.textContent('text=One-Off Soaps') === "One-Off Soaps";

});
