// playwright.config.js
// @ts-check
const { devices } = require('@playwright/test');
/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  testDir: 'tests',
  testDir: '../browser-automated-tests-playwright',
  timeout: 180000,
  retries: 2,
  use: {
    baseURL: 'http://127.0.0.1:5000',
    headless: false,
    viewport: { width: 1280, height: 720 },
    launchOptions: {
      slowMo: 1000,
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

module.exports = config;
