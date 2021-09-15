
const { test, expect } = require('@playwright/test');
//Subscribie tests
test("452_show-owner_category_creation", async ({ page }) => {
  try{
    console.log("checking if category is already created...");
    await page.goto('/');
    page.setDefaultTimeout(3000);
    const category_exists = await page.textContent("text=basic plan")
    if (category_exists === "basic plan") {
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('checking-if-category-is-created.png');
        console.log("category created, exiting test");
        return 0
          }
      } catch (e) {
        console.log("Continuing with category creation");
      }
     // Go to add category
    await page.goto('/admin/add-category');

     //creating category
    console.log("creating category");
    await page.fill("input[name='category']", 'basic plan');
    await page.click('text="Save"');
    expect(await page.screenshot()).toMatchSnapshot('creating-category.png');

    const category_created = await page.content("#alert-heading");
    expect(category_created === "Notification");
      // adding plans to category
    console.log("adding plans to category");
    await page.click("[name='basic plan-category']");
    const category_plans = await page.textContent("text=Category - Assign Plan");
    expect(category_plans === "Category - Assign Plan");

    await page.click("text=Hair Gel");
    await new Promise(x => setTimeout(x, 1000));
    await page.click("text=Bath Soaps");
    await new Promise(x => setTimeout(x, 1000));
    await page.click("text=One-Off Soaps");
    await new Promise(x => setTimeout(x, 1000));

    expect(await page.screenshot()).toMatchSnapshot('adding-plans-to-category.png');
    await page.click('text="Save"');

    const plans_added = await page.content("#alert-heading");
    expect(plans_added === "Notification");

      // checking if category was created. 
    await page.goto('/');
    const category_added = await page.content("text=basic plan");
    expect(category_added === "basic plan");
    expect(await page.screenshot()).toMatchSnapshot('category-created.png');
    console.log("the category created");

  });