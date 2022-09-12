const { test, expect } = require('@playwright/test');

//Subscribie tests
test.describe("Subscribie tests:", () => {
  test.beforeEach(async ({ page }) => {
    //Login
    await page.goto('/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    
    const content = await page.textContent('.card-title')
    expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin
  }); 
  //Stripe Test
  test("@293@connect-to-stripe@shop-owner@Stripe Test", async ({ page }) => {
    // Go to Stripe Connect payment gateways page
    await page.goto('admin/connect/stripe-connect');
    // Check onboarding not already completed
    try {
      let connectYourShopContent = await page.evaluate(() => document.body.textContent);
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
  test("@293@connect-to-stripe@shop-owner@detect stripe onboarding page", async ({ page }) => {

      // Go to Stripe Connect payment gateways page
      await page.goto('admin/connect/stripe-connect');
      //page.setDefaultTimeout(3000);
      let contentStripeConnect = await page.evaluate(() => document.body.textContent);
      test.skip(contentStripeConnect.indexOf("Congrats!") > -1);
      expect(await page.screenshot()).toMatchSnapshot('stripe_status.png');

      // deleting connect account id, if stripe was not succesfully connected
      await page.goto('/admin/delete-connect-account');
      await page.goto('/admin/dashboard');
      console.log('deleting connect account id');

      // Start Stripe connect onboarding
      await page.goto('/admin/connect/stripe-connect');
      await page.click('.btn-success');

      console.log("Start Stripe connect onboarding")

        const phone_email_content = await page.textContent('.db-ConsumerUITitle');
        // Stripe onboarding login
        if (expect(phone_email_content === "Get paid by Subscribie")) {
          console.log("Detected stripe onboarding")
          // Use the text phone number for SMS verification
          await page.click('text="the test phone number"');
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
        const personal_details_content = await page.textContent('text="Verify your personal details"');
        if (expect(personal_details_content === 'Verify your personal details')) {
          await new Promise(x => setTimeout(x, 1000));
          try {
              await page.fill('#first_name', "Sam");
              await page.fill('#last_name', "Smith");
              try {
                await page.fill('input[name=dob-day]', "28", { timeout: 10000 });
                await page.fill('input[name=dob-month]', "12", { timeout: 10000 });
                await page.fill('input[name=dob-year]', "1990", { timeout: 10000 });
                console.log("input selector being used");
              } catch (e) {
                await page.selectOption('select >> nth=0', '12');
                await page.selectOption('select >> nth=1', '28');
                await page.selectOption('select >> nth=2', '1990');
                console.log("select selector being used");
              }

          } catch (e) {
            console.log("Exception in setting personal details, perhaps already completed");
            console.log(e);
            console.log("Continuing regardless");
          }
          await page.fill('input[name=address]', "123 Tree Lane");
          await page.fill('input[name=locality]', "123 Tree Lane");
          await page.fill('input[name=zip]', "SW1A 1AA");
          await page.fill('input[name=phone]', "0000000000");
          await page.click('text="Continue"');
        }
        // Stripe onboarding industry selection
        //const business_details_content = await page.textContent('.db-ConsumerUITitle');
        const business_details_content = await page.textContent('text="Tell us a few details about how you earn money with Subscribie."');
        if (expect(business_details_content === "Tell us a few details about how you earn money with Subscribie.")) {
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
          //await page.click('button:has-text("Update")');
          await page.locator('text="Update"').click();
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

          // Dont wait too long to click either Submit or Done
          try {
            await page.click('button:has-text("Submit")', { timeout: 10000 })
            console.log("Clicking Submit");
          } catch (e) {
            await page.click('button:has-text("Done")');
            console.log("Clicking Done");
          }
        }

      console.log("Announce stripe account automatically visiting announce url. In prod this is called via uwsgi cron");
      await new Promise(x => setTimeout(x, 5000));
      const stripe_connected = await page.textContent("text=Congrats!");
      expect(stripe_connected === "Congrats!");
      console.log("Stripe Connected");
      await page.goto('/admin/announce-stripe-connect'); 
      await page.textContent(':has-text("Announced Stripe connect account")') === "Announced Stripe connect account";
      console.log("Announced to Stripe connect account");

  }); 
  order_plan_with_only_recurring_charge = require('./tests/293_subscriber_order_plan_with_only_recurring_charge');

  order_plan_with_only_upfront_charge = require('./tests/293_subscriber_order_plan_with_only_upfront_charge');

  order_plan_with_free_trial = require('./tests/475_subscriber_order_plan_with_free_trial');
  // When you run order subscription and upfront charge, it will run 2 more tests that are inside:
  // 1. Transacion filter by name and plan title
  // 2. 2.A pause, resume and 2.B cancel subscription test. 
  order_plan_with_subscription_and_upfront_charge = require('./tests/293_subscriber_order_plan_with_recurring_and_upfront_charge');

});

