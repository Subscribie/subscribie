const { test, expect } = require('@playwright/test');
const checkNewSubscriberEmail= require('./checkNewSubscriberEmail.js');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;


test('@1226@shop-owner@check new subscriber email', async ({ page }) => {

  // Adding admin email
  await page.goto("/admin/add-shop-admin"); // Go to home before selecting product
  await page.fill('[name=email]', SUBSCRIBER_EMAIL_USER);
  await page.fill('[name=password]', 'password');
  await page.click("text=Save");

  //checkout to plan
  await page.goto("/"); // Go to home before selecting product
  await page.click('[name="Free plan"]');

  // Fill in order form
  await page.fill('#given_name', 'John');
  await page.fill('#family_name', 'Smith');
  await page.fill('#email', "test@example.com");
  await page.fill('#mobile', '07123456789');
  await page.fill('#address_line_one', '123 Short Road');
  await page.fill('#city', 'London');
  await page.fill('#postcode', 'L01 T3U');
  expect(await page.screenshot()).toMatchSnapshot('new-customer-form.png');
  await page.click('text="Continue to Payment"');

  const order_complete_content = await page.textContent('.title-1');
  expect(order_complete_content === "Order Complete!");
  expect(await page.screenshot()).toMatchSnapshot('recurring-order-complete.png');

  await new Promise(r => setTimeout(r, 10000));
  checkNewSubscriberEmail.checkNewSubscriberEmail();
  console.log("checking new subscriber email template");
  await new Promise(r => setTimeout(r, 5000));
  const subscriber_name = checkNewSubscriberEmail.subscriber_name;
  expect(subscriber_name === "John Smith");
  
});
