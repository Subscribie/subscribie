const { test, expect } = require('@playwright/test');
const checkNewSubscriberEmail= require('./checkNewSubscriberEmail.js');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;
const { admin_login } = require('./features/admin_login');

test('@1226@shop-owner@check new subscriber email', async ({ page }) => {

  await admin_login(page);
  await page.goto("/admin/add-shop-admin"); // Go to home before selecting product
  await page.fill('[name=email]', SUBSCRIBER_EMAIL_USER);
  await page.fill('[name=password]', 'password');
  await page.click("text=Save");
  console.log("Ordering plan with only recurring charge...");
  // Buy item with subscription & upfront fee
  await page.goto("/"); // Go to home before selecting product
  await page.click('[name="Bath Soaps"]');

  // Fill in order form
  await page.fill('#given_name', 'John');
  await page.fill('#family_name', 'Smith');
  await page.fill('#email', 'hello@example.com');
  await page.fill('#mobile', '07123456789');
  await page.fill('#address_line_one', '123 Short Road');
  await page.fill('#city', 'London');
  await page.fill('#postcode', 'L01 T3U');
  await page.click('.btn-primary-lg');
  // Begin stripe checkout
  const order_summary_content = await page.textContent(".title-1");
  expect(order_summary_content === "Order Summary");
  await page.click('#checkout-button');

  //Verify first payment is correct (recuring charge only)
  const payment_content = await page.textContent('div.mr2.flex-item.width-fixed');
  expect(payment_content === "£10.99");
  const recuring_charge_content = await page.textContent('.Text-fontSize--16');
  expect(recuring_charge_content === "Subscribe to Bath Soaps");

  // Pay with test card
  await page.fill('#cardNumber', '4242 4242 4242 4242');
  await page.fill('#cardExpiry', '04 / 24');
  await page.fill('#cardCvc', '123');
  await page.fill('#billingName', 'John Smith');
  await page.selectOption('select#billingCountry', 'GB');
  await page.fill('#billingPostalCode', 'LN1 7FH');
  await page.click('.SubmitButton');
  const order_complete_content = await page.textContent('.title-1');
  expect(order_complete_content === "Order Complete!");
  expect(await page.screenshot()).toMatchSnapshot('recurring-order-complete.png');

  await new Promise(r => setTimeout(r, 10000));
  checkNewSubscriberEmail.checkNewSubscriberEmail();
  console.log("checking new subscriber email template");
  await new Promise(r => setTimeout(r, 10000));
  const subscriber_name = checkNewSubscriberEmail.subscriber_name;
  expect(subscriber_name === "John Smith");
  
});
