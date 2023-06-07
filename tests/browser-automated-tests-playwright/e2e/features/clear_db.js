const { admin_login } = require('./admin_login');
const { expect } = require('@playwright/test');
const  URL = process.env['PLAYWRIGHT_HOST'];
var clear_db = async function (page) {
    await page.goto(URL + '/admin/remove-subscriptions');
    const contentSubscriptions = await page.evaluate(() => document.body.textContent.indexOf("all subscriptions deleted"));
    expect(contentSubscriptions > -1);

    await page.goto(URL + '/admin/remove-people');
    const contentPeople = await page.evaluate(() => document.body.textContent.indexOf("all people deleted"));
    expect(contentPeople > -1);

    await page.goto(URL + '/admin/remove-transactions');
    const contentTransactions = await page.evaluate(() => document.body.textContent.indexOf("all transactions deleted"));
    expect(contentTransactions > -1);

    await page.goto(URL + '/admin/remove-documents');
    const contentDocuments = await page.evaluate(() => document.body.textContent.indexOf("all documents deleted"));
    expect(contentDocuments > -1);
    // End Clear DB
}

module.exports.clear_db = clear_db
