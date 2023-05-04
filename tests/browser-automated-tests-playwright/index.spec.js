const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe.parallel("Subscribie tests:", () => {
  test.beforeEach(async ({ page }) => {
    //Login
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    
    const content = await page.textContent('.card-title')
    expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
  });
  const plan_creation = require('./tests/shop_owner_plan_creation');
  
  const changing_plans_order = require('./tests/275_shop_owner_changing_plans_order');

  const share_private_plan_url = require('./tests/491_shop_owner_share_private_plan_url');
  
  const categories_creation = require('./tests/452_shop_owner_categories_creation');

  const private_page_creation = require('./tests/334_shop_owner_private_page_creation');

  const public_page_creation = require('./tests/121_shop_owner_public_page_creation');

  const slogan_creation = require('./tests/212_shop_owner_slogan_creation');

  const change_shop_colour = require('./tests/387_shop_owner_change_shop_colour');

  const uploading_plan_picture = require('./tests/872_uploading_plan_picture.js');

  const adding_vat = require('./tests/463_shop_owner_adding_vat');

  const order_plan_with_choice_options_and_required_note = require('./tests/264_subscriber_order_plan_with_choice_options_and_required_note');

  const order_plan_with_cancel_at = require('./tests/516_subscriber_order_plan_with_cancel_at');

  const order_plan_cooling_off = require('./tests/133_subscriber_order_plan_with_cooling_off');
 
  const order_plan_with_only_recurring_charge = require('./tests/293_subscriber_order_plan_with_only_recurring_charge');

  const order_plan_with_only_upfront_charge = require('./tests/293_subscriber_order_plan_with_only_upfront_charge');

  const order_plan_with_free_trial = require('./tests/475_subscriber_order_plan_with_free_trial');
  // Verify that as a shop owner i can see the terms and conditions attached
  const order_plan_with_subscription_and_upfront_charge = require('./tests/293_subscriber_order_plan_with_recurring_and_upfront_charge');
  // When you run order subscription and upfront charge, it will run 2 more tests that are inside:
  // 1. Transacion filter by name and plan title
  // 2. 2.A pause, resume and 2.B cancel subscription test. 

  const ordering_plan_with_VAT = require('./tests/463_subscriber_ordering_plan_with_VAT');

  const subscriber_magic_login = require('./tests/623_subscriber_magic_login');

  const shop_owner_terms_and_conditions_creation = require('./tests/1005_shop_owner_terms_and_conditions_creation.js');

  const subscriber_order_free_plan = require('./tests/939_subscriber_order_free_plan_with_terms_and_conditions.js');

  const subscriber_terms_and_condition_check_test = require('./tests/1005_subscriber_terms_and_condition_check_test.js');

  const subscriber_change_card_details = require('./tests/993_subscriber_change_card_details.js');

});
