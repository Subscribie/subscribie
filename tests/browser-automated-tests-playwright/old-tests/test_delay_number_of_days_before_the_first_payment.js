const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;

/* Test transactions can be query by plan title and name */
async function test_delay_number_of_days_before_the_first_payment(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_delay_number_of_days_before_the_first_payment");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS});
    const context = await browser.newContext(browserContextOptions);
    context.setDefaultTimeout(15000);
    const page = await context.newPage();
    
    // Login and verify order appears in admin dashboard
    // Login
    await page.goto(PLAYWRIGHT_HOST + 'auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    await page.screenshot({ path: `logged-in-${browserType}.png` });
    // Assert logged in OK
    const content = await page.textContent('.card-title');
    assert(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
    
    // Go to add plan page
    // Crude wait before we check subscribers to allow webhooks time
    await new Promise(x => setTimeout(x, 1000)); // 1 secconds
    await page.goto(PLAYWRIGHT_HOST + 'admin/add');
    await page.screenshot({ path: `add-plan-${browserType}.png` });
    
    //Fill plan 
    await page.fill('#title-0', 'Cooling off plan');
    await page.fill('#selling_points-0-0', 'cooling');
    await page.fill('#selling_points-0-1', 'off');
    await page.fill('#selling_points-0-3', 'plan');

    await page.click('.form-check-input');
    //wait for the recurring charge to expand
    const monthly_content = await page.textContent('#interval_amount_label');
    assert(monthly_content === "Recurring Amount");
    await page.fill('#interval_amount-0', '10');
    await page.fill('#days_before_first_charge-0','10');
    await new Promise(x => setTimeout(x, 1000));

    await page.click('text="Save"');
    await page.goto(PLAYWRIGHT_HOST);

    //verify in edit plans
    await new Promise(x => setTimeout(x, 1000)); // 1 secconds
    await page.goto(PLAYWRIGHT_HOST + 'admin/edit');
    const cooling_off_plan = await page.textContent('text="Cooling off plan"');
    assert(cooling_off_plan === 'Cooling off plan');

    await page.click('text="Cooling off plan"');

    const cooling_off_content = await page.textContent('text="Cooling off plan"');
    assert(cooling_off_content === "Cooling off plan");

    // Logout of shop owners admin dashboard
    await page.goto(PLAYWRIGHT_HOST + 'auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    assert(logged_out_content === "You have logged out");
 
    await browser.close();
  }
};

module.exports = test_delay_number_of_days_before_the_first_payment
