// playwright.config.js
// @ts-check


require('dotenv').config()
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_SLOWMO = parseInt(process.env.PLAYWRIGHT_SLOWMO);
const { devices } = require('@playwright/test');
/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: 'tests',
  testDir: '../browser-automated-tests-playwright',
  timeout: 180000,
  retries: 2,
  use: {
    baseURL: PLAYWRIGHT_HOST,
    headless: PLAYWRIGHT_HEADLESS,
    viewport: { width: 1280, height: 720 },
    launchOptions: {
      slowMo: PLAYWRIGHT_SLOWMO,
    },
    video:"on",
    },
  projects: [
   // {
   //  name: 'Desktop Chromium',
   //   use: {
   //     browserName: 'chromium',
   //   },
   // },
    // Test against mobile viewports.
    {
      name: 'Mobile Safari',
      use: devices['iPhone 12'],
    },
  ],
};
console.log(PLAYWRIGHT_HOST)
console.log(PLAYWRIGHT_HEADLESS)
console.log(PLAYWRIGHT_SLOWMO)
module.exports = config;
