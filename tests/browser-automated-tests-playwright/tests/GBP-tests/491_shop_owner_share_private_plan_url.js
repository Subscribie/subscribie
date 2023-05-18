const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe("Looking for Private plan share URL:", () => {
    test("@491@shop-owner@Create Private Plan @GBP", async ({ page }) => {
        await page.goto('/admin/edit');
        page.setDefaultTimeout(3000);
        const private_plan__already_exist = await page.textContent('text="First Private plan"');
        if (private_plan__already_exist === 'First Private plan') {
        await new Promise(x => setTimeout(x, 1000));
        page.click("text='First Private plan'")
        page.click("text=Private plan Plan or Product name Plan name is required. Product selling points  >> a")
        await new Promise(x => setTimeout(x, 5000));
        const monthly_content = await page.textContent('text="First Private plan"');
        expect(monthly_content === "First Private plan");
        expect(await page.screenshot()).toMatchSnapshot('Private-plan-share-url.png');
        console.log("Private plan share URL working")
        }
    });
});