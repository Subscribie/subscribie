const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
  //Login
  await page.goto('/auth/login');
  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'password');
  await page.click('#login');
  
  const content = await page.textContent('.card-title')
  expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin

  await new Promise(x => setTimeout(x, 5000));
}); 

  const plan_creation = require('./tests/shop_owner_plan_creation');
  
  const changing_plans_order = require('./tests/275_shop_owner_changing_plans_order');

  const share_private_plan_url = require('./tests/491_shop_owner_share_private_plan_url');

  const order_plan_with_choice_options_and_required_note = require('./tests/264_subscriber_order_plan_with_choice_options_and_required_note');

  const order_plan_with_cancel_at = require('./tests/516_subscriber_order_plan_with_cancel_at');

  const order_plan_cooling_off = require('./tests/133_subscriber_order_plan_with_cooling_off');

  const enabling_donations = require('./tests/1065_shop_owner_enabling_donations');
  
  const checkout_donations = require('./tests/1065_subscriber_checkout_donation');
