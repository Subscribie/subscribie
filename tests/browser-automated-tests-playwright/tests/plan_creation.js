const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe("Plan Creation tests:", () => {
      // Create cooling off plan
  test("Create cooling off plan", async ({ page }) => {
    console.log("Starting plan creations...");
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
  test("Create Private Plan", async ({ page }) => {
    console.log("Creating Private Plan");
    await page.goto('/admin/edit');
    try {
      page.setDefaultTimeout(3000);
      const private_plan__already_exist = await page.textContent('text="Private plan"');
      if (private_plan__already_exist === 'Private plan') {
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('Private-plan-already-created.png');
        console.log("Private plan already created, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Continuing with Private plan creation");
    }
     // Go to add plan page
     await page.goto('/admin/add');

     //Fill plan 
     await page.fill('#title-0', 'Private plan');
     await page.fill('#selling_points-0-0', 'This is a');
     await page.fill('#selling_points-0-1', 'Private');
     await page.fill('#selling_points-0-3', 'plan');
     await page.click('.form-check-input');

     //wait for the recurring charge to expand
     const monthly_content = await page.textContent('#interval_amount_label');
     expect(monthly_content === "Recurring Amount");
     await page.fill('#interval_amount-0', '15');

     await page.click('#private');
     await page.click('text="Save"');

     await page.goto('/admin/edit');
     page.setDefaultTimeout(3000);
     const private_plan_exist = await page.textContent('text="Private plan"');
     if (private_plan_exist === 'Private plan') {
         await new Promise(x => setTimeout(x, 1000));
         expect(await page.screenshot()).toMatchSnapshot('Private-plan-was-created.png');
         console.log("Private plan was created, exiting test");
     }
     await page.goto('/');
     let private_plan_content = await page.evaluate(() => document.body.textContent);
     if (private_plan_content.indexOf("Private plan") > 1) {
      console.log("ERROR: Private plan is not Private")
     }
     else {
      console.log("Private plan is not in home page (Success)")
     }
  });

});

//module.exports = plan_creation;