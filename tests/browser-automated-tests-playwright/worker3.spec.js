const { test, expect } = require('@playwright/test');

test.beforeEach(async ({ page }) => {
    //Login
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    
    const content = await page.textContent('.card-title')
    expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
  }); 
  const clear_DB = require('./tests/clear_db');

  const categories_creation = require('./tests/452_shop_owner_categories_creation');

  const private_page_creation = require('./tests/334_shop_owner_private_page_creation');

  const public_page_creation = require('./tests/121_shop_owner_public_page_creation');

  const slogan_creation = require('./tests/212_shop_owner_slogan_creation');

  const change_shop_colour = require('./tests/387_shop_owner_change_shop_colour');

  const uploading_plan_picture = require('./tests/872_uploading_plan_picture.js');

  const adding_vat = require('./tests/463_shop_owner_adding_vat');

  const ordering_plan_with_VAT = require('./tests/463_subscriber_ordering_plan_with_VAT');

  const subscriber_magic_login = require('./tests/623_subscriber_magic_login');

  const subscriber_order_free_plan = require('./tests/939_subscriber_order_free_plan.js');
  const subscriber_change_card_details = require('./tests/993_subscriber_change_card_details.js');
