import { test } from '@playwright/test';
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const testName = "@1333-1_subscriber_order_free_plan_with_question_attached";

test(testName, async ({ page }) => {

  await admin_login(page);
  await set_test_name_cookie(page, testName);

  await page.goto('/admin/dashboard');
  await page.getByRole('button', { name: 'Questions (Simple Forms)' }).click();
  await page.getByRole('link', { name: 'Add / Edit / Delete Questions' }).click();
  await page.getByRole('cell', { name: 'Where did you hear about us?' }).first().click();
  await page.getByRole('button', { name: 'Assign Plan' }).first().click();
  await page.getByLabel('Free plan').check();
  await page.getByRole('button', { name: 'Save' }).click();
  await page.getByRole('navigation').getByRole('link', { name: 'Soap Subscription 2025-01-' }).click();
  await page.getByRole('heading', { name: 'Free plan with question attached' }).click();
  await page.getByRole('link', { name: 'Choose' }).nth(4).click();
  await page.getByPlaceholder('Please enter...').click();
  await page.getByPlaceholder('Please enter...').fill('The Grapevine');
  await page.locator('form').filter({ hasText: 'The Free plan plan has 1' }).getByRole('button').click();
  await page.getByPlaceholder('John', { exact: true }).click();
  await page.getByPlaceholder('John', { exact: true }).fill('Fred');
  await page.getByPlaceholder('John', { exact: true }).press('Tab');
  await page.getByPlaceholder('Smith', { exact: true }).fill('Blogs');
  await page.getByPlaceholder('Smith', { exact: true }).press('Tab');
  await page.getByPlaceholder('johnsmith@gmail.com').fill('fred@example.com');
  await page.getByPlaceholder('johnsmith@gmail.com').press('Tab');
  await page.getByPlaceholder('+').fill('00000000000');
  await page.locator('#new_customer div').filter({ hasText: 'Address' }).nth(2).click();
  await page.locator('#address_line_one').fill('123');
  await page.locator('#address_line_one').press('Tab');
  await page.locator('#city').fill('Newcastle Upon Tyne');
  await page.locator('#city').press('Tab');
  await page.locator('#postcode').fill('00000000000');
  await page.getByRole('button', { name: 'Continue to Payment' }).click();
  await page.getByRole('link', { name: 'Dashboard' }).click();
  await page.goto('/admin/subscribers');
  await page.locator('details').filter({ hasText: 'Question Answers Where did' }).getByRole('strong').first().click();
  await page.getByText('Where did you hear about us?: The Grapevine').first().click();
});