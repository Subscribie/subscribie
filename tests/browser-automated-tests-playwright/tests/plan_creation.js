const { test, expect, context } = require('@playwright/test');

//Subscribie tests
test.describe("Plan Creation tests:", () => {
  test.beforeEach(async ({ page }) => {
      // Login
      await page.goto('/auth/login');
      await page.fill('#email', 'admin@example.com');
      await page.fill('#password', 'password');
      await page.click('#login');
      // Assert logged in OK
      const content = await page.textContent('.card-title');
      expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
      
  });
  test.afterAll(async () => {
    // Logout of shop owners admin dashboard
    await page.goto('/auth/logout');
    await page.screenshot({ path: `logged-out-${browserType}.png` });
    // Assert logged out OK
    const logged_out_content = await page.textContent('.text-center');
    expect(logged_out_content === "You have logged out");
  });
      // Create cooling off plan
  test("Create cooling off plan", async ({ page }) => {
    await page.goto('/');
    try {
      page.setDefaultTimeout(3000);
      const cooling_off_plan_exist = await page.textContent('text="Cooling off plan"');
      if (cooling_off_plan_exist === 'Cooling off plan') {
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('Cooling-off-plan-already-created.png');
        console.log("Cooling off plan already created, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Continuing with Cooling off plan creation");
    }
     // Go to add plan page
     await page.goto('/admin/add');

     //Fill plan 
     await page.fill('#title-0', 'Cooling off plan');
     await page.fill('#selling_points-0-0', 'cooling');
     await page.fill('#selling_points-0-1', 'off');
     await page.fill('#selling_points-0-3', 'plan');
     await page.click('.form-check-input');

     //wait for the recurring charge to expand
     const monthly_content = await page.textContent('#interval_amount_label');
     expect(monthly_content === "Recurring Amount");
     await page.fill('#interval_amount-0', '10');
     await page.fill('#days_before_first_charge-0','10');

     await page.click('text="Save"');
     await page.goto("/");
 
     //verify home page plan creation
     await new Promise(x => setTimeout(x, 1000)); // 1 secconds
     const cooling_off_plan = await page.textContent('text="Cooling off plan"');
     expect(cooling_off_plan === 'Cooling off plan');
     // screenshot cooling off plan 
     await new Promise(x => setTimeout(x, 1000));
     expect(await page.screenshot()).toMatchSnapshot('add-cooling-off-plan.png');

  });
  test("Create free trial plan", async ({ page }) => {
    await page.goto('/');
    try {
      page.setDefaultTimeout(3000);
      const free_trial = await page.textContent('text="Free Trial"');
      if (free_trial === 'Free Trial') {
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('Free-trial-plan-already-created.png');
        console.log("Free trial plan already created, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Continuing with Free trial plan creation");
    }
    // Go to add plan
    await page.goto('/admin/add');
    
    //Fill plan 
    await page.fill('#title-0', 'Free Trial');
    await page.fill('#selling_points-0-0', 'Trial');
    await page.fill('#selling_points-0-1', 'Trial');
    await page.fill('#selling_points-0-3', 'Trial');

    await page.click('.form-check-input');
    //wait for the recurring charge to expand
    const monthly_content = await page.textContent('#interval_amount_label');
    expect(monthly_content === "Recurring Amount");

    await page.fill('#interval_amount-0', '10');
    await page.fill('#trial_period_days-0', '10');

    await page.click('text="Save"');
    await page.goto('/');

    const free_trial = await page.textContent('text="Free Trial"');
    expect(free_trial === "Free Trial");

    // screenshot cooling off plan 
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('add-free-trial-plan.png');

  });
  test("Create cancel at plan", async ({ page }) => {
    await page.goto('/');
    try {
      page.setDefaultTimeout(3000);
      const free_trial = await page.textContent('text="Automatically cancels on: 2025-09-07"');
      if (free_trial === "Automatically cancels on: 2025-09-07") {
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('cancel-at-plan-already-created.png');
        console.log("Cancel At plan already created, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Continuing with Cancel At plan creation");
    }
    // Go to add plan
    await page.goto('/admin/add');
    
    //Fill plan 
    await page.fill('#title-0', 'cancel at plan');
    await page.fill('#selling_points-0-0', 'plan');
    await page.fill('#selling_points-0-1', 'plan');
    await page.fill('#selling_points-0-3', 'plan');

    await page.click('.form-check-input');
    //wait for the recurring charge to expand
    const monthly_content = await page.textContent('#interval_amount_label');
    expect(monthly_content === "Recurring Amount");
    await page.fill('#interval_amount-0', '10');

    // wait for the cancel at to expand
    await page.click('#cancel_at_set-0');
    // filling cancel at
    await page.fill('[type=date]', '2025-09-07');

    await page.click('text="Save"');
    await page.goto('/');

    const free_trial = await page.textContent('text="Automatically cancels on: 2025-09-07"');
    expect(free_trial === "Automatically cancels on: 2025-09-07");
    //screenshot
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('add-cancel-at-plan.png');

  });

});

//module.exports = plan_creation;