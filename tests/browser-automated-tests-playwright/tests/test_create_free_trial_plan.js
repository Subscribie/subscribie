const playwright = require('playwright');
const assert = require('assert');
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const fs = require('fs');
const videosDir = __dirname + '/videos/';
/* Test transactions can be query by plan title and name */
async function test_add_free_trial_plan(browsers, browserContextOptions) {
  for (const browserType of browsers) {
    console.log("test_add_free_trial_plan");
    const browser = await playwright[browserType].launch({headless: PLAYWRIGHT_HEADLESS, slowMo: 1000});
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
    const content = await page.textContent('.card-title')
    assert(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
    
    // Go to My Subscribers page
    // Crude wait before we check subscribers to allow webhooks time
    await new Promise(x => setTimeout(x, 1000)); // 5 secconds
    await page.goto(PLAYWRIGHT_HOST + 'admin/add')
    await page.screenshot({ path: `add-plan-${browserType}.png` });
    
    //Fill plan 
    await page.fill('#title-0', 'Free Trial');
    await page.fill('#selling_points-0-0', 'Trial');
    await page.fill('#selling_points-0-1', 'Trial');
    await page.fill('#selling_points-0-3', 'Trial');

    await page.click('.form-check-input');
    //wait for the recurring charge to expand
    const monthly_content = await page.textContent('#interval_amount_label');
    assert(monthly_content === "Recurring Amount");

    await page.fill('#interval_amount-0', '10');
    await page.fill('#trial_period_days-0', '10');
    
    await new Promise(x => setTimeout(x, 1000));
    await page.click('text="Save"');
    await page.goto(PLAYWRIGHT_HOST);

    const free_trial = await page.textContent('text="Free Trial"');
    assert(free_trial === "Free Trial");

    // Logout of shop owners admin dashboard
    await page.goto(PLAYWRIGHT_HOST + 'auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    assert(logged_out_content === "You have logged out");

    // renaming video file
    currentVideoFile= await page.video().path();
    fs.renameSync(currentVideoFile, videosDir + "test_create_free_trial_plan.webm");
    videoName = fs.readdirSync(videosDir).find(name => name.endsWith('test_create_free_trial_plan.webm'));
    console.log(videoName);
 
    await browser.close();
  }
};

module.exports = test_add_free_trial_plan
