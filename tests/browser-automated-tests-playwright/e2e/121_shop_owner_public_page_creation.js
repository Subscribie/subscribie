const { test, expect } = require('@playwright/test');

test("@121@shop-owner@Creating Public Page", async ({ page }) => {
        page.setDefaultTimeout(5000);
        await page.goto('/page/contactus');
        await new Promise(x => setTimeout(x, 5000));
        let checking_public_page_content = await page.evaluate(() => document.body.textContent);
        if (checking_public_page_content.indexOf("contact-us") > -1) {
            expect(await page.screenshot()).toMatchSnapshot('public-page-already-checked.png');
            console.log("Public page already set, exiting test");
            test.skip();
          }
         
        console.log("Continuing with Public page creation");
        await page.goto('/pages/add-page');
        page.setDefaultTimeout(3000);
        await page.fill("input[name='page-title']", 'contact-us');
        await page.fill("div[role='textbox']", 'contact information');
        await page.click('text="Save"');
        const page_created = await page.content("#alert-heading");
        expect(page_created === "Notification");
        console.log("Page already created");
        
        //visiting public page
        await page.goto('/page/contactus');
        await new Promise(x => setTimeout(x, 3000));
        const public_page_created = await page.content("#title-1");
        expect(public_page_created === "contact-us");
        
});