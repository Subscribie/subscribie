const { test, expect } = require('@playwright/test');
const checkShopOwnerLogin = require('./checkShopOwnerLogin.js');

const SHOP_OWNER_LOGIN_URL = process.env.SHOP_OWNER_LOGIN_URL
const SHOP_OWNER_EMAIL = process.env.SHOP_OWNER_EMAIL_USER

test('@704@shop_owner@magic login receives email @GBP', async ({ page }) => {
  await page.goto(SHOP_OWNER_LOGIN_URL);
  await page.fill('#email', SHOP_OWNER_EMAIL);
  await page.click('#login');
  await new Promise(r => setTimeout(r, 5000));
  checkShopOwnerLogin.checkShopOwnerLogin();
  console.log(checkShopOwnerLogin.magic_login_url);
  await new Promise(r => setTimeout(r, 5000));
  await page.goto(checkShopOwnerLogin.magic_login_url);
  await new Promise(r => setTimeout(r, 5000));
});
