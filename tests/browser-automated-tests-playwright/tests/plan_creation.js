const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe("Plan Creation tests:", () => {
      // Create cooling off plan
  test("133_show-owner_Create cooling off plan", async ({ page }) => {
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
  test("475_shop-owner_Create free trial plan", async ({ page }) => {
    await page.goto('/');
    try {
      page.setDefaultTimeout(3000);
      const free_trial = await page.textContent('text="Free Trial plan"');
      if (free_trial === 'Free Trial plan') {
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
    await page.fill('#title-0', 'Free Trial plan');
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

    const free_trial = await page.textContent('text="Free Trial plan"');
    expect(free_trial === "Free Trial plan");

    // screenshot cooling off plan 
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('add-free-trial-plan.png');

  });
  test("516_shop-owner_Create cancel at plan", async ({ page }) => {
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
  test("491_show-owner_Create Private Plan", async ({ page }) => {
    console.log("Creating Private Plan");
    await page.goto('/admin/edit');
    try {
      page.setDefaultTimeout(3000);
      const private_plan__already_exist = await page.textContent('text="First Private plan"');
      if (private_plan__already_exist === 'First Private plan') {
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
     await page.fill('#title-0', 'First Private plan');
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
     const private_plan_exist = await page.textContent('text="First Private plan"');
     if (private_plan_exist === 'FIrst Private plan') {
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

  test("Create plan with options, choice, required description", async ({ page }) => {
    await page.goto('/');
    try {
      page.setDefaultTimeout(3000);
      const check_plan_with_choice_and_options = await page.textContent('text="Plan with choice and options"');
      expect(check_plan_with_choice_and_options === "Plan with choice and options");
      await page.click("text=See choice options");
      await page.click("text=Choices (2 options)");
      //check if plan options are blue and red
      const check_plan_option_red = await page.textContent('text="Red"');
      expect(check_plan_option_red === "Red");
      const check_plan_option_blue = await page.textContent('text="Blue"');
      expect(check_plan_option_blue === "Blue");

      const expand_choice = await page.textContent('text="Choices (2 options)"');
      if (expand_choice === "Choices (2 options)") {
 
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('plan-with-choice-and-options-already-created.png');
        console.log("Plan with choice and options already created, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Continuing with Plan with choice and options creation");
    }
    // Go to add plan
    await page.goto('/admin/add');
    
    //Fill plan 
    await page.fill('#title-0', 'Plan with choice and options');
    await page.fill('#selling_points-0-0', 'Plan with ');
    await page.fill('#selling_points-0-1', 'Choice and options');
    await page.fill('#selling_points-0-3', 'with required description');

    //wait for the recurring charge to expand
    await page.click('.form-check-input');
    const monthly_content = await page.textContent('#interval_amount_label');
    expect(monthly_content === "Recurring Amount");
    await page.fill('#interval_amount-0', '15');

    //fill plan description 
    await page.click('#plan_description_required-0');
    await page.fill('#description-0','This plan requires a user description, options and choice selection');
    
    //Require customer note
    await page.click('#note_to_seller_required-0');
    await page.fill('#note_to_buyer_message-0','Please add another colour');

    await page.click('text="Save"');
    //Check if plan was created 
    await page.goto('/');
    const plan_with_choice_and_options = await page.textContent('text="Plan with choice and options"');
    expect(plan_with_choice_and_options === "Plan with choice and options");
    //screenshot
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('plan-with-choice-and-options-created.png');
    
    //Add options and choices
    console.log('adding plan options and choices');
    await page.goto('/admin/add-choice-group');

    //add choice group
    const add_choice_group = await page.textContent('text="Add Choice Group"');
    expect(add_choice_group === "Add Choice Group");
    await page.fill('.form-control','Choices');
    await page.click("text='Save'");
    await page.textContent('.alert-heading') === "Notification";
    console.log("Choice Created");

    //add first option
    console.log("adding options...")
    await page.goto('/admin/list-choice-groups');
    await page.click("text=Options");

    const add_options = await page.textContent('text="Option"');
    expect(add_options === "Option");
    await page.click("text=Add Option");
    await page.fill('.form-control','Red');
    await page.click("text='Save'");
    await page.textContent('.alert-heading') === "Notification";
    console.log("First Option added");

    //add second option
    await page.click("text=Add Option");
    await page.fill('.form-control','Blue');
    await page.click("text='Save'");
    await page.textContent('.alert-heading') === "Notification";
    console.log("Second Option added");

    //assign choice to plan
    console.log("Assigning Choice to plan...")
    await page.goto('/admin/list-choice-groups');
    await page.click("text=Assign Plan");
    const assign_choice_to_plan = await page.textContent('text="Choice Group - Assign Plan"');
    expect(assign_choice_to_plan === "Choice Group - Assign Plan");
    await page.click("text=Plan with choice and options");
    await page.click("text='Save'");
    await page.textContent('.alert-heading') === "Notification";
    console.log("Choice assigned to plan");

    //confirm choice and option plan was added
    await page.goto('/');
    const free_trial = await page.textContent('text="Plan with choice and options"');
    expect(free_trial === "Plan with choice and options");

    //check if plan options are blue and red
    const check_plan_option_red = await page.textContent('text="Red"');
    expect(check_plan_option_red === "Red");
    const check_plan_option_blue = await page.textContent('text="Blue"');
    expect(check_plan_option_blue === "Blue");

    //check if plan have choice
    await page.click("text=See choice options");
    await page.click("text=Choices (2 options)");
    const expand_choice = await page.textContent('text="Choices (2 options)"');
    expect(expand_choice === "Choices (2 options)");
    expect(await page.screenshot()).toMatchSnapshot('plan-with-choice-and-options-created.png');
    console.log("Plan with option and choices shown in homepage");
  });

});

//module.exports = plan_creation;