const { test, expect } = require('@playwright/test');
test("619_shop-owner_transaction filter by name and by plan title", async ({ page }) => {
    console.log("transaction filter by name and by plan title");
    //Login
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');

    const content = await page.textContent('.card-title')
    expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
    // Verify transaction is present in 'All transactions page'

    await page.goto('admin/transactions')
    const transaction_content = await page.textContent('.transaction-amount');
    expect (transaction_content == '£6.99');

    // Verify subscriber is linked to the transaction:
    const transaction_subscriber_content = await page.textContent('.transaction-subscriber');
    expect (transaction_subscriber_content === 'John smith');
      // Verify search by Name - Transaccions
    await page.fill('input[name=subscriber_name]',"John");
    await page.click('.btn-primary');
    expect (transaction_subscriber_content === 'John smith');
    expect(await page.screenshot()).toMatchSnapshot('filter-by-name.png');

      // Verify search by plan title 
    await page.fill('input[name=plan_title]',"Hair");
    await page.click('.btn-primary');
    expect (transaction_subscriber_content === 'John smith');
    expect(await page.screenshot()).toMatchSnapshot('filter-by-plan.png');

      // Verify search by Name & plan title
    await page.fill('input[name=subscriber_name]',"John");
    await page.fill('input[name=plan_title]',"Hair");
    await page.click('.btn-primary');
    expect (transaction_subscriber_content === 'John smith');
    expect(await page.screenshot()).toMatchSnapshot('filter-by-name-and-plan.png');
});

