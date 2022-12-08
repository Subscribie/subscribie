const { test, expect } = require('@playwright/test');
const TEST = process.env.TEST;
//Subscribie tests
test.describe("Subscribie tests:", () => {
  test.beforeEach(async ({ page }) => {
    //Login
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    
    const content = await page.textContent('.card-title')
    expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
  }); 
  //Stripe Test
  test("@293@connect-to-stripe@shop-owner@Stripe Test", async ({ page }) => {
    // Go to Stripe Connect payment gateways page
    await page.goto('admin/connect/stripe-connect');
    // Check onboarding not already completed
    try {
      let connectYourShopContent = await page.evaluate(() => document.body.textContent);
      if (connectYourShopContent.indexOf("Your currently running in test mode.") > -1) {
        expect(await page.screenshot()).toMatchSnapshot('connect_stripe-to-shop-dashboard-chromium.png');
        console.log("Already connected Stripe sucessfully, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Exception checking if onboarding completed, looks like it's not complete");
      console.log("Continuing with Stripe Connect onboarding");
    }
  });
  const stripe_connect = require(`./tests/${TEST}/stripe_connect.js`);

  const order_plan_with_only_recurring_charge = require(`./tests/${TEST}/293_subscriber_order_plan_with_only_recurring_charge`);

  const order_plan_with_only_upfront_charge = require(`./tests/${TEST}/293_subscriber_order_plan_with_only_upfront_charge`);

  const order_plan_with_free_trial = require(`./tests/${TEST}/475_subscriber_order_plan_with_free_trial`);
  // When you run order subscription and upfront charge, it will run 2 more tests that are inside:
  // 1. Transacion filter by name and plan title
  // 2. 2.A pause, resume and 2.B cancel subscription test. 
  const order_plan_with_subscription_and_upfront_charge = require(`./tests/${TEST}/293_subscriber_order_plan_with_recurring_and_upfront_charge`);

});

