const { test, expect } = require('@playwright/test');

test("Changing Plans order", async ({ page }) => {
    console.log("Changing plans order...");
    await page.goto("/admin/edit")
    const check_plan_with_choice_and_options = await page.textContent('text="Edit Plans"');
    expect(check_plan_with_choice_and_options === "Edit Plans");

    //change order with recurring and upfront
    await page.click("text=Hair Gel");
    await page.fill("#position-0", "0");
    console.log("Hair Gel plan order changed");

    //change order with only recurring
    await page.click("text=Bath Soaps");
    await page.fill("#position-1", "1");
    console.log("Bath Soaps plan order changed");

    //change order with only upfront
    await page.click("text=One-Off Soaps");
    await page.fill("#position-2", "2");
    console.log("One-Off Soaps plan order changed");

    //change order with cooling off
    await page.click("text=Cooling off plan");
    await page.fill("#position-3", "3");
    console.log("Cooling off plan order changed");

    //change order with free trial 
    await page.click("text=Free Trial plan");
    await page.fill("#position-4", "4");
    console.log("Free Trial plan order changed");

    //change order with cancel at
    await page.click("text=cancel at plan");
    await page.fill("#position-5", "5");
    console.log("cancel at plan order changed");

    //change order with private plan
    await page.click("text=First Private plan");
    await page.fill("#position-6", "6");
    console.log("Private plan order changed");

    //change order with choices and options
    await page.click("text=Plan with choice and options");
    await page.fill("#position-7", "7");
    console.log("choice and options plan order changed");

    await page.click("text=Save");

});