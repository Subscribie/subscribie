const { test, expect } = require('@playwright/test');
const checkShopOwnerLogin = require('./checkShopOwnerLogin.js');

const TEST_SHOP_OWNER_LOGIN_URL = process.env.TEST_SHOP_OWNER_LOGIN_URL_ISSUE_704
const TEST_SHOP_OWNER_EMAIL = process.env.TEST_SHOP_OWNER_EMAIL_ISSUE_704

test('@704@shop_owner@magic login receives email', async ({ page }) => {
  await page.goto(TEST_SHOP_OWNER_LOGIN_URL);
  await page.fill('#email', TEST_SHOP_OWNER_EMAIL);
  await page.click('#login');
  await new Promise(r => setTimeout(r, 5000));
  checkShopOwnerLogin.checkShopOwnerLogin();
  await new Promise(r => setTimeout(r, 5000));
});
