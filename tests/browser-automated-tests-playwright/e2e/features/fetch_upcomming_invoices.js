var fetch_upcomming_invoices = async function (page) {
    // Go to upcoming payments and ensure plan is attached to upcoming invoice
    await page.goto('/admin/upcoming-invoices');
    await new Promise(x => setTimeout(x, 35000));
    await page.click('#fetch_upcoming_invoices');
    await new Promise(x => setTimeout(x, 30000));
    await page.goto('/admin/upcoming-invoices');
}

module.exports.fetch_upcomming_invoices = fetch_upcomming_invoices;