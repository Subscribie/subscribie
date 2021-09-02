const { test, expect } = require('@playwright/test');

test.describe("order plan with only recurring charge test:", () => {
    test("Ordering recurring plan", async ({ page }) => {
        console.log("Ordering plan with only recurring charge...");
        // Buy item with subscription & upfront fee
        await page.goto("/"); // Go to home before selecting product
        await page.click('[name="Bath Soaps"]');

        // Fill in order form
        await page.fill('#given_name', 'John');
        await page.fill('#family_name', 'Smith');
        await page.fill('#email', 'john@example.com');
        await page.fill('#mobile', '07123456789');
        await page.fill('#address_line_one', '123 Short Road');
        await page.fill('#city', 'London');
        await page.fill('#postcode', 'L01 T3U');
        expect(await page.screenshot()).toMatchSnapshot('recurring-new-customer-form.png');
        await page.click('.btn-primary-lg');
        // Begin stripe checkout
        const order_summary_content = await page.textContent(".title-1");
        expect(order_summary_content === "Order Summary");
        expect(await page.screenshot()).toMatchSnapshot('recurring-pre-stripe-checkout.png');
        await page.click('#checkout-button');

        //Verify first payment is correct (recuring charge only)
        const payment_content = await page.textContent('div.mr2.flex-item.width-fixed');
        expect(payment_content === "£10.99");
        const recuring_charge_content = await page.textContent('.Text-fontSize--16');
        expect(recuring_charge_content === "Subscribe to Bath Soaps");

        // Pay with test card
        await page.fill('#cardNumber', '4242 4242 4242 4242');
        await page.fill('#cardExpiry', '04 / 24');
        await page.fill('#cardCvc', '123');
        await page.fill('#billingName', 'John Smith');
        await page.selectOption('select#billingCountry', 'GB');
        await page.fill('#billingPostalCode', 'LN1 7FH');
        expect(await page.screenshot()).toMatchSnapshot('recurring-stripe-checkout-filled.png');
        await page.click('.SubmitButton');
    
        // Verify get to the thank you page order complete
        await new Promise(x => setTimeout(x, 5000)); //5 secconds
        const order_complete_content = await page.textContent('.title-1');
        expect(order_complete_content === "Order Complete!");
        expect(await page.screenshot()).toMatchSnapshot('recurring-order-complete.png');

        // Go to My Subscribers page
        // Crude wait before we check subscribers to allow webhooks time
        await new Promise(x => setTimeout(x, 5000)); //5 secconds
        await page.goto('/admin/subscribers')
        expect(await page.screenshot()).toMatchSnapshot('recurring-view-subscribers.png');
        
        // Click Refresh Subscription
        await page.click('#refresh_subscriptions'); // this is the refresh subscription
        await page.textContent('.alert-heading') === "Notification";
        // screeshot to the active subscriber
        await page.goto('admin/dashboard');
        expect(await page.screenshot()).toMatchSnapshot('recurring-active-subscribers.png');
        // go back to subscriptions
        await page.goto('/admin/subscribers')
        
        // Verify that subscriber is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === 'john@example.com');

        // Verify that plan is attached to subscriber
        const subscriber_plan_title_content = await page.textContent('.subscription-title');
        expect(subscriber_plan_title_content === 'Bath Soaps');

        const content_subscriber_plan_interval_amount = await page.textContent('.subscribers-plan-interval_amount');
        expect(content_subscriber_plan_interval_amount === '£10.99');

        const subscriber_plan_sell_price_content = await page.evaluate(() => document.querySelector('.subscribers-plan-sell-price').textContent.indexOf("(No up-front fee)"));
        expect(subscriber_plan_sell_price_content > -1)
        
        // Go to upcoming payments and ensure plan is attached to upcoming invoice
        await page.goto('/admin/upcoming-invoices');
        // Fetch Upcoming Invoices
        await page.click('#fetch_upcoming_invoices');
        await new Promise(x => setTimeout(x, 10000)); //10 secconds
        const content_upcoming_invoice_plan_price_interval = await page.textContent('.plan-price-interval');
        expect(content_upcoming_invoice_plan_price_interval === '£10.99');

        const content_upcoming_invoice_plan_sell_price = await page.textContent('.upcoming-invoices-plan-no-sell_price');
        expect(content_upcoming_invoice_plan_sell_price === '(No up-front cost)');
    });
});

