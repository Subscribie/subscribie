import { test, expect } from '@playwright/test';
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const testName = "@1333_shop_owner_add_free_text_question";

test(testName, async ({ page }) => {
  await admin_login(page);
  await set_test_name_cookie(page, testName);
  await page.goto("/admin/dashboard");
  await page.getByRole('button', { name: 'Questions (Simple Forms)' }).click();
  await page.getByRole('link', { name: 'Add / Edit / Delete Questions' }).click();
  await page.getByRole('link', { name: 'Add Question' }).click();
  await page.getByRole('textbox').click();
  await page.getByRole('textbox').fill('Where did you hear about us?');
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByRole('cell', { name: 'Where did you hear about us?' }).first().click();
});