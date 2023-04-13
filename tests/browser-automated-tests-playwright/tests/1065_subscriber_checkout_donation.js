const { test, expect } = require('@playwright/test');
const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER;

test.describe("checkout a donation:", () => {
    test("@1065@subscriber@checkout a donation", async ({ page }) => {
        console.log("Ordering plan with only upfront charge...");
        // Checkout a Donation
        await page.goto('/donate'); // Go to home before selecting product

        // Fill in the donation form
        await page.fill('#given_name', 'John');
        await page.fill('#family_name', 'Smith');
        await page.fill('#email', SUBSCRIBER_EMAIL_USER);
        await page.fill('#mobile', '07123456789');
        await page.fill('#address_line_one', '123 Short Road');
        await page.fill('#city', 'London');
        await page.fill('#postcode', 'L01 T3U');
        await page.fill('#donation_amount', "10.55");
        expect(await page.screenshot()).toMatchSnapshot('donation-new-customer-form.png');
        await page.click('role=button[name="Donate"]');

        // Begin stripe checkout
        const order_summary_content = await page.textContent(".title-1");
        expect(order_summary_content === "Donation Summary");
        expect(await page.screenshot()).toMatchSnapshot('donation-pre-stripe-checkout.png');
        await page.click('#checkout-button');

        //Verify first payment is correct (donation charge)
        const first_payment_content = await page.textContent('#ProductSummary-totalAmount');
        expect(first_payment_content === "£10.55");
        const upfront_charge_content = await page.textContent('.Text-fontSize--16');
        expect(upfront_charge_content === "Donation");

        // Pay with test card
        await page.fill('#cardNumber', '4242 4242 4242 4242');
        await page.fill('#cardExpiry', '04 / 24');
        await page.fill('#cardCvc', '123');
        await page.fill('#billingName', 'John Smith');
        await page.selectOption('select#billingCountry', 'GB');
        await page.fill('#billingPostalCode', 'LN1 7FH');
        expect(await page.screenshot()).toMatchSnapshot('donation-stripe-checkout-filled.png');
        await page.click('.SubmitButton');
    
        // Verify get to the thank you page order complete
        const order_complete_content = await page.textContent('.title-1');
        expect(order_complete_content === "Order Complete!");
        expect(await page.screenshot()).toMatchSnapshot('donation-order-complete.png');

        // Go to transactions page
        await new Promise(x => setTimeout(x, 5000)); //5 seconds
        await page.goto('/admin/transactions')
        expect(await page.screenshot()).toMatchSnapshot('donation-view-subscribers.png');

        // Verify that the Donation column is enabled inside the transactions table
        const donation_transaction_enabled = await page.textContent('role=cell[name="Donation"]');
        expect(donation_transaction_enabled === "Donation");

        // Verify that the transaction was a donation
        const checkout_is_a_donation = await page.textContent('role=cell[name="True"]');
        expect(checkout_is_a_donation === 'True');
        

        //clicking donations in the dashboard
        await page.goto('/admin/subscribers?action=show_donors')

        // Verify that donor is present in the list
        const subscriber_email_content = await page.textContent('.subscriber-email');
        expect(subscriber_email_content === SUBSCRIBER_EMAIL_USER);

        // Verify that is a donation
        const donor_title_content = await page.textContent('.donation-title');
        expect(donor_title_content === 'Donations');
        expect(await page.screenshot()).toMatchSnapshot('donation-subscribers.png');
        await new Promise(x => setTimeout(x, 1000));


    });
});
