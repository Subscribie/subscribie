const { test, expect } = require('@playwright/test');
// Clear DB before each test.
test("Clearing the DB", async ({ page }) => {

    await page.goto('/admin/remove-subscriptions');
    const contentSubscriptions = await page.evaluate(() => document.body.textContent.indexOf("all subscriptions deleted"));
    expect(contentSubscriptions > -1);
    
    await page.goto('/admin/remove-people');
    const contentPeople = await page.evaluate(() => document.body.textContent.indexOf("all people deleted"));
    expect(contentPeople > -1);

    await page.goto('/admin/remove-transactions');
    const contentTransactions = await page.evaluate(() => document.body.textContent.indexOf("all transactions deleted"));
    expect(contentTransactions > -1);

}); 