const { test, expect } = require('@playwright/test');

test("Creating Private Page", async ({ page }) => {

        await page.goto('/page/privatetestpage');
        await new Promise(x => setTimeout(x, 5000));
        let checking_private_page_content = await page.evaluate(() => document.body.textContent);
        if (checking_private_page_content.indexOf("This is a Private Page") > -1) {
            expect(await page.screenshot()).toMatchSnapshot('Private-page-already-checked.png');
            console.log("Private plan already set, exiting test");
            test.skip();
          }
         
        console.log("Continuing with Private page creation");
        await page.goto('/pages/add-page');
        page.setDefaultTimeout(3000);
        await page.fill("input[name='page-title']", 'Private Test Page');
        await page.fill("div[role='textbox']", 'This is a Private Page');
        await page.click('text="Save"');
        const page_created = await page.content("#alert-heading");
        expect(page_created === "Notification");
        console.log("Page already created, now configuring to private");
        await new Promise(x => setTimeout(x, 3000));

        await page.goto('/pages/private-pages');
        const private_page_feature = await page.content("text='Update Private Pages'");
        expect(private_page_feature === "Update Private Pages");
        page.click("input[type=checkbox]");
        await new Promise(x => setTimeout(x, 2000));
        page.click("text='Submit'");
        await new Promise(x => setTimeout(x, 2000));

        const private_page_created = await page.content("#alert-heading");
        expect(private_page_created === "Notification");
        console.log("Private Page created");

        await page.goto('/page/privatetestpage');
        await new Promise(x => setTimeout(x, 2000));
        const visiting_private_page = await page.textContent("text='This is a Private Page'");
        expect(visiting_private_page === "This is a Private Page");
        console.log("Private Page succedded");

        console.log("Logging out to check for the private page");
        await page.goto('/auth/logout');
        const log_out = await page.content("text='You have logged out'");
        expect(log_out === "You have logged out");
        console.log("Logged out");

        await page.goto('/page/privatetestpage');
        await new Promise(x => setTimeout(x, 3000));
        let private_page_content = await page.evaluate(() => document.body.textContent);
        if (private_page_content.indexOf("This is a Private Page") > -1) {
            console.log("ERROR: the page is not private")
            return 1
          }
        else {
            console.log("Private Page not avaliable for the public.(Succeded)");
        }
});