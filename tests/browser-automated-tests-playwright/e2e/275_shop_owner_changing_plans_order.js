const { test, expect } = require('@playwright/test');

test("@275@shop-owner@Changing Plans order", async ({ page }) => {
    console.log("Changing plans order...");
    await page.goto("/admin/edit")
    const check_plan_with_choice_and_options = await page.textContent('text="Edit Plans"');
    expect(check_plan_with_choice_and_options === "Edit Plans");

    //change order with recurring and upfront
    await page.click("text=Hair Gel");
    await page.fill('[data-plan-name-position="Hair Gel"]', '0');
    console.log("Hair Gel plan order changed");

    //change order with only recurring
    await page.click("text=Bath Soaps");
    await page.fill('[data-plan-name-position="Bath Soaps"]', '1');
    console.log("Bath Soaps plan order changed");

    //change order with only upfront
    await page.click("text=One-Off Soaps");
    await page.fill('[data-plan-name-position="One-Off Soaps"]', '2');
    console.log("One-Off Soaps plan order changed");

    //change order with cooling off
    await page.click("text=Cooling off plan");
    await page.fill('[data-plan-name-position="Cooling off plan"]', '3');
    console.log("Cooling off plan order changed");

    //change order with free trial 
    await page.click("text=Free Trial plan");
    await page.fill('[data-plan-name-position="Free Trial plan"]', '4');
    console.log("Free Trial plan order changed");

    //change order with cancel at
    await page.click("text=cancel at plan");
    await page.fill('[data-plan-name-position="cancel at plan"]', '5');
    console.log("cancel at plan order changed");

    //change order with choices and options
    await page.click("text=Plan with choice and options");
    await page.fill('[data-plan-name-position="Plan with choice and options"]', '6');
    console.log("choice and options plan order changed");

    await page.click("text=Save");

});