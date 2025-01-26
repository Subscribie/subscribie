import { test, expect } from '@playwright/test';
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const { admin_login } = require('./features/admin_login');

test('test', async ({ page }) => {
  await admin_login(page);
  await set_test_name_cookie(page, "@1431_shop_owner_bulk_pause_payment_collection_all_subscribers");
  await page.goto('/admin/dashboard');
  await page.getByRole('button', { name: 'My Subscribers' }).click();
  await page.getByRole('link', { name: 'Pause all Subscribers payment' }).click();
  await page.getByRole('link', { name: 'Pause payment collection for' }).click();
  await page.getByRole('link', { name: 'Yes' }).click();
  await page.getByText('All payment collections are').click();
  await expect(page.getByText('All payment collections are being paused in the background. You can move away from this page.')).toBeVisible();
  await page.goto('/admin/dashboard');
  await page.getByRole('button', { name: 'My Subscribers' }).click();
  await page.getByRole('link', { name: 'View Subscribers' }).click();
  await page.getByRole('button', { name: 'Refresh Subscriptions' }).click();
  await page.waitForTimeout(3000);
  await page.goto('/admin/subscribers');
  await page.getByText('Paused - (keep_as_draft)').first().click();
  await page.getByText('Paused - (keep_as_draft)').nth(1).click();
});