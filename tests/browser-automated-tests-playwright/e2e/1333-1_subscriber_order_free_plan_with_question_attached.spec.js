import { test } from '@playwright/test';
const { admin_login } = require('./features/admin_login');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');

const testName = "@1333-1_subscriber_order_free_plan_with_question_attached";

test(testName, async ({ page }) => {

  await admin_login(page);
  await set_test_name_cookie(page, testName);

  await page.goto('/');
  await page.locator('.pricing-plan').filter({hasText: "Free plan with question attached"}).first().getByRole('link').click();
  await page.getByPlaceholder('Please enter...').click();
  await page.getByPlaceholder('Please enter...').fill('The Grapevine');
  await page.locator('form').filter({ hasText: 'The Free plan with question' }).getByRole('button').click();
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