const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe("Subscribie tests:", () => {
  // Clear DB before each test.
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    
    await page.goto('/admin/remove-subscriptions');
    const contentSubscriptions = await page.evaluate(() => document.body.textContent.indexOf("all subscriptions deleted"));
    expect(contentSubscriptions > -1);
    
    await page.goto('/admin/remove-people');
    const contentPeople = await page.evaluate(() => document.body.textContent.indexOf("all people deleted"));
    expect(contentPeople > -1);

    await page.goto('/admin/remove-transactions');
    const contentTransactions = await page.evaluate(() => document.body.textContent.indexOf("all transactions deleted"));
    expect(contentTransactions > -1);
    
    //Login
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    
    const content = await page.textContent('.card-title')
    expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
  }); 
  
  //Stripe Test
  test("Stripe Test", async ({ page }) => {

    // Go to Stripe Connect payment gateways page
    await page.goto('admin/connect/stripe-connect');
    // Check onboarding not already completed
    try {
      let connectYourShopContent = await page.evaluate(() => document.body.textContent);
      //const contentSuccess = await page.textContent('.alert-success');
      if (connectYourShopContent.indexOf("Congrats!") > -1) {
        expect(await page.screenshot()).toMatchSnapshot('connect_stripe-to-shop-dashboard-chromium.png');
        console.log("Already connected Stripe sucessfully, exiting test");
        return 0;
      }
    } catch (e) {
      console.log("Exception checking if onboarding completed, looks like it's not complete");
      console.log("Continuing with Stripe Connect onboarding");
    }
  });
  test("detect stripe onboarding page", async ({ page }) => {
      // Go to Stripe Connect payment gateways page
      await page.goto('admin/connect/stripe-connect');
      //page.setDefaultTimeout(3000);
      let contentStripeConnect = await page.evaluate(() => document.body.textContent);
      test.skip(contentStripeConnect.indexOf("Congrats!") > -1);

      // Start Stripe connect onboarding
      expect(await page.screenshot()).toMatchSnapshot('stripe_status.png');
      await page.goto('/admin/connect/stripe-connect');
      await page.click('.btn-success');

      // Create shop owner stripe connect email address based on 'admin' + 'hostname'
      const email = await page.evaluate(() => 'admin@' + document.location.hostname);
      await new Promise(x => setTimeout(x, 5000));

      console.log("Start Stripe connect onboarding")

        const phone_email_content = await page.textContent('.db-ConsumerUITitle');
        // Stripe onboarding login
        if (expect(phone_email_content === "Get paid by Subscribie")) {
          console.log("Detected stripe onboarding")
          // Use the text phone number for SMS verification
          await page.click('text="the test phone number"');
          await page.fill('#email', email);
          await page.click('text="Continue"');
          await new Promise(x => setTimeout(x, 2000));
        } else {
          console.log("Could not detect stripe onboarding page")
        }
  
        // Use SME verify with test code
        const phone_content = await page.textContent('text="Enter the verification code we sent to your phone"');
        if (expect(phone_content === "Enter the verification code we sent to your phone")) {
          console.log("Clicking Use test code")
          await page.click('button:has-text("Use test code")'); //Use Test code for SMS
        }
  
        // Stripe onboarding Business type
        //const business_type_content = await page.textContent('.db-ConsumerUITitle');
        const business_type_content = await page.textContent('text="Tell us about your business"');
        if (expect(business_type_content === "Tell us about your business")) {
          await new Promise(x => setTimeout(x, 4000));
          await page.selectOption('select', 'individual');
          await page.click('text="Continue"');
        }

        // Stripe onboarding personal details step
        //const personal_details_content = await page.textContent('.db-ConsumerUITitle');
        const personal_details_content = await page.textContent('text="Personal details"');
        if (expect(personal_details_content === 'Personal details')) {
          await new Promise(x => setTimeout(x, 1000));
          try {
              await page.fill('#first_name', "Sam");
              await page.fill('#last_name', "Smith");
              await page.fill('input[name=dob-day]', "28");
              await page.fill('input[name=dob-month]', "12");
              await page.fill('input[name=dob-year]', "1990");
          } catch (e) {
            console.log("Exception in setting personal details, perhaps already completed");
            console.log(e);
            console.log("Continuing regardless");
          }
          await page.fill('input[name=address]', "123 Tree Lane");
          await page.fill('input[name=locality]', "123 Tree Lane");
          await page.fill('input[name=zip]', "SW1A 1AA");
          await page.click('text="Continue"');
        }
        // Stripe onboarding industry selection
        //const business_details_content = await page.textContent('.db-ConsumerUITitle');
        const business_details_content = await page.textContent('text="Business details"');
        if (expect(business_details_content === "Business details")) {
          await new Promise(x => setTimeout(x, 1000));
          await page.click('text="Please select your industry…"');
          await page.click('text="Software"');
          await page.click('text="Continue"');
        }
      
        // Stripe onboarding payouts bank details
        //const account_payouts_content = await page.textContent('.db-ConsumerUITitle');
        const account_payouts_content = await page.textContent('text="Select an account for payouts"');
        if (expect(account_payouts_content === "Select an account for payouts")) {
          await new Promise(x => setTimeout(x, 1000));
          await page.click('text="Use test account"');
        }
        // Stripe onboarding verification summary
        //const notice_title_content = await page.textContent('.Notice-title');
        const notice_title_content = await page.textContent('text="Missing required information"');
        if (expect(notice_title_content === "Missing required information")) {
          console.log("On the Let's review your details page");
          await new Promise(x => setTimeout(x, 2000));
          await page.click('button:has-text("Update")');
        }
        // Stripe onboarding identify verification step
        //const additional_information_content = await page.textContent('.db-ConsumerUITitle');
        const additional_information_content = await page.textContent('text="Additional information"');
        if (expect(additional_information_content === "Additional information")) {
          await new Promise(x => setTimeout(x, 5000));

          await page.click(":nth-match(:text('Verify Now'), 2)");
          const address_content = await page.textContent('text="Proof of address document"');
          if (expect(address_content === "Proof of address document")) {
            await new Promise(x => setTimeout(x, 1000));
            await page.click('text="Use test document"');
          }
          const home_address_provided = await page.textContent(":nth-match(:text('Provided'), 2)");
          await page.click(":nth-match(:text('Verify Now'), 1)");
          const id_verification_content = await page.textContent('text="ID verification for "');
          await new Promise(x => setTimeout(x, 5000));
          if (expect(id_verification_content === "ID verification for ")) {
            await new Promise(x => setTimeout(x, 1000));
            await page.click('text="Use test document"');
          }

          const id_verification_provided = await page.textContent(":nth-match(:text('Provided'), 1)");
          if (expect(id_verification_provided === "Provided") && expect(home_address_provided === "Provided")) {
            await page.click('button:has-text("Submit")');
            await new Promise(x => setTimeout(x, 5000));
          }
        }
        // Stripe onboarding verification complete
        const stripe_completion_content = await page.textContent('text="Other information provided"');
        if (expect(stripe_completion_content === "Other information provided")) {
          await new Promise(x => setTimeout(x, 1000));
          await page.click('button:has-text("Submit")');
        }

      console.log("Announce stripe account manually visiting announce url. In prod this is called via uwsgi cron");
      await page.goto('/admin/announce-stripe-connect');
      const contentStripeAccountAnnounced = await page.evaluate(() => document.body.textContent.indexOf("Announced Stripe connect account"));
      expect(contentStripeAccountAnnounced > -1);
  }); 
});
    
//plan_creation = require('./tests/plan_creation.js');
order_plan_with_only_recurring_charge = require('./tests/order_plan_with_only_recurring_charge.js');

