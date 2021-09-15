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
  clear_DB = require('./tests/clear_db');

  categories_creation = require('./tests/categories_creation');

  private_page_creation = require('./tests/private_page_creation');

  public_page_creation = require('./tests/public_page_creation');

  slogan_creation = require('./tests/slogan_creation');