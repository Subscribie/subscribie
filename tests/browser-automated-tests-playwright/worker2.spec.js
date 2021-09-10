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

  plan_creation = require('./tests/plan_creation');
  
  changing_plans_order = require('./tests/changing_plans_order');

  share_private_plan_url = require('./tests/share_private_plan_url');

  order_plan_with_choice_options_and_required_note = require('./tests/order_plan_with_choice_options_and_required_note');

  order_plan_with_cancel_at = require('./tests/order_plan_with_cancel_at');

  order_plan_cooling_off = require('./tests/order_plan_with_cooling_off');


