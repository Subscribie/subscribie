const { test, expect } = require('@playwright/test');

//Subscribie tests
test("212_show-owner_slogan creation", async ({ page }) => {
    console.log("checking if slogan is already created...");
    await page.goto('/');
    page.setDefaultTimeout(3000);
    let slogan_exists = await page.evaluate(() => document.body.textContent);
    if (slogan_exists === 'this is a slogan') {
        await new Promise(x => setTimeout(x, 1000));
        expect(await page.screenshot()).toMatchSnapshot('slogan-already-created.png');
        console.log("slogan already created, exiting test");
        test.skip();
          }
     // Go to edit plan page
    await page.goto('/admin/edit');

     //edit slogan
    await page.fill("input[name='slogan']", 'this is a slogan');
    await page.click("text=Hair Gel");
    await page.click('text="Save"');

     //verify home page plan creation
    await page.goto("/");
    await new Promise(x => setTimeout(x, 1000)); // 1 secconds
    const slogan_created = await page.textContent('text=this is a slogan');
    expect(slogan_created === 'this is a slogan');
     // screenshot cooling off plan 
    await new Promise(x => setTimeout(x, 1000));
    expect(await page.screenshot()).toMatchSnapshot('slogan-created.png');

  });