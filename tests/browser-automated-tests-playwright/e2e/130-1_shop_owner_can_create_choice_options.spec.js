import { test } from '@playwright/test';
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const testName = "@130-1_shop_owner_can_create_choice_options";

test(testName, async ({ page }) => {
  await admin_login(page);
  await set_test_name_cookie(page, testName);
  await page.goto('/admin/dashboard');
  await page.getByRole('button', { name: 'Choice Groups' }).click();
  await page.getByRole('link', { name: 'Add / Edit / Delete Choice' }).click();
  await page.getByRole('link', { name: 'Add Choice Group' }).click();
  await page.getByRole('textbox').click();
  await page.getByRole('textbox').fill('Colour Choice');
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByRole('button', { name: 'Options' }).first().click();
  await page.getByRole('link', { name: 'Add Option' }).first().click();
  await page.getByRole('textbox').click();
  await page.getByRole('textbox').fill('Red');
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByRole('link', { name: 'Add Option' }).click();
  await page.getByRole('textbox').click();
  await page.getByRole('textbox').fill('Blue');
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByRole('cell', { name: 'Red' }).first().click();
  await page.getByRole('cell', { name: 'Blue' }).first().click();
  await page.getByRole('link', { name: 'Options' }).first().click();
  await page.getByRole('link', { name: 'Choice Groups' }).first().click();
  await page.getByRole('cell', { name: 'Colour Choice' }).first().click();
});