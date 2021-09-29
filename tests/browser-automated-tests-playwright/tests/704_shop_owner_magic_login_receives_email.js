const { test, expect } = require('@playwright/test');
const checkShopOwnerLogin = require('./checkShopOwnerLogin.js');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const TEST_SHOP_OWNER_EMAIL = process.env.email_user;


test('@704@shop_owner@magic login receives email', async ({ page }) => {
  await page.goto("/auth/login");
  await page.fill('#email', TEST_SHOP_OWNER_EMAIL);
  await page.click('#login');
  await new Promise(r => setTimeout(r, 5000));
  checkShopOwnerLogin.checkShopOwnerLogin();
  console.log(checkShopOwnerLogin.magic_login_url);
  await new Promise(r => setTimeout(r, 5000));
  console.log(checkShopOwnerLogin.magic_login_url);
  await page.goto(checkShopOwnerLogin.magic_login_url);
  await new Promise(r => setTimeout(r, 5000));
});
