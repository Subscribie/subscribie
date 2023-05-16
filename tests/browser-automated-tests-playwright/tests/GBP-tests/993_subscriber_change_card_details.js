const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;


test('@993@subscriber@change card details @GBP', async ({ page }) => {

  
  await page.goto("/auth/logout");
  await page.goto("/account/logout");
  //login in as subscriber
  await page.goto("/account/login");
  await page.fill('#email', SUBSCRIBER_EMAIL_USER);
  await page.fill('#password', 'password');
  await page.click('text=Sign In');
  await page.textContent('.card-title') === "Your subscriptions";
  console.log("Logged in as a subscriber");
  //check cards details
  await page.click("text= Update Payment Method");
  await page.textContent('text=Save card information') === "Save card information";
  // Pay with test card
  await page.fill('#cardNumber', '5555 5555 5555 4444');
  await page.fill('#cardExpiry', '04 / 28');
  await page.fill('#cardCvc', '123');
  await page.fill('#billingName', 'John Smith');
  await page.selectOption('select#billingCountry', 'GB');
  await page.fill('#billingPostalCode', 'LN1 7FH');
  await page.click('.SubmitButton');
  console.log("changing card details");
  // check the details have changed
  const default_payment_updated = await page.textContent("text=Default payment method updated");
  expect(default_payment_updated === "Default payment method updated");
  const card_details = await page.textContent("text=4444");
  expect(default_payment_updated === "4444");
  console.log("card details updated succesfully");
  

});
