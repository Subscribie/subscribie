// global-setup.js
const { test, expect, chromium } = require('@playwright/test');

module.exports = async config => {
  const { baseURL, storageState } = config.projects[0].use;
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(baseURL + '/auth/login');
  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'password');
  await page.click('#login');
  
  const content = await page.textContent('.card-title')
  expect(content === 'Checklist'); // If we see "Checklist", we're logged in to admin

  await new Promise(x => setTimeout(x, 5000));
  await page.goto(baseURL + '/admin/delete-connect-account');
  console.log('deleting-connect-account-id');
  await new Promise(x => setTimeout(x, 2000)); //2 secconds
  await page.goto(baseURL + 'admin/dashboard')
  const connect_to_stripe = await page.textContent('text="Review Stripe"');
  expect (connect_to_stripe == 'Review Stripe');
  console.log('stripe is not connected');

  await page.context().storageState({ path: storageState });
  await browser.close();
};
