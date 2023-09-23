const { test, expect } = require('@playwright/test');
const { set_test_name_cookie } = require('./features/set_test_name_cookie');
const { admin_login } = require('./features/admin_login');

test("@619@shop_owner @619_shop_owner_transaction_filter_by_name_and_by_plan_title", async ({ page }) => {
  console.log("@619_shop_owner_transaction_filter_by_name_and_by_plan_title");
  await set_test_name_cookie(page, "@619_shop_owner_transaction_filter_by_name_and_by_plan_title");

  await admin_login(page);

  await page.goto("admin/dashboard")
  const content = await page.textContent('.card-title')
  expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
  // Verify transaction is present in 'All transactions page'

  await page.goto('admin/transactions')
  const transaction_content = await page.textContent('.transaction-amount');
  expect(transaction_content == '£6.99');

  // Verify subscriber is linked to the transaction:
  const transaction_subscriber_content = await page.textContent('.transaction-subscriber');
  expect(transaction_subscriber_content === 'John smith');
  // Verify search by Name - Transaccions
  await page.fill('input[name=subscriber_name]', "John");
  await page.click('.btn-primary');
  expect(transaction_subscriber_content === 'John smith');

  // Verify search by plan title 
  await page.fill('input[name=plan_title]', "Hair");
  await page.click('.btn-primary');
  expect(transaction_subscriber_content === 'John smith');

  // Verify search by Name & plan title
  await page.fill('input[name=subscriber_name]', "John");
  await page.fill('input[name=plan_title]', "Hair");
  await page.click('.btn-primary');
  expect(transaction_subscriber_content === 'John smith');
});

