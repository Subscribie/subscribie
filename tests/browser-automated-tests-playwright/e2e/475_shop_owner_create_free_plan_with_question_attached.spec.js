import { test } from '@playwright/test';
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const testName = "@475_shop_owner_create_free_plan_with_question_attached";


test('@475_shop_owner_create_free_plan_with_question_attached', async ({ page }) => {
  await admin_login(page);
  await set_test_name_cookie(page, testName);
  await page.goto('/admin/dashboard');
  await page.getByRole('link', { name: 'Add plan' }).click();
  await page.getByLabel('Plan or Product name What are').click();
  await page.getByLabel('Plan or Product name What are').fill('Free plan with question attached');
  await page.locator('#selling_points-0-0').click();
  await page.locator('#selling_points-0-0').fill('a');
  await page.locator('#selling_points-0-0').press('Tab');
  await page.locator('#selling_points-0-1').fill('b');
  await page.locator('#selling_points-0-1').press('Tab');
  await page.locator('#selling_points-0-3').fill('c');
  await page.getByLabel('Plan Description', { exact: true }).check();
  await page.getByLabel('Plan description', { exact: true }).click();
  await page.getByLabel('Plan description', { exact: true }).fill('A free plan with a question attached.');
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByRole('button', { name: 'Questions (Simple Forms)' }).click();
  await page.getByRole('link', { name: 'Add / Edit / Delete Questions' }).click();
  await page.getByRole('button', { name: 'Assign Plan' }).first().click();
  await page.getByLabel('Free plan with question').first().check();
  await page.getByRole('button', { name: 'Save' }).click();
});