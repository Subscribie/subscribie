// playwright.config.js
// @ts-check
require('dotenv').config()
import { PlaywrightTestConfig } from '@playwright/test';
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const TEST = process.env.TEST;
const PLAYWRIGHT_SLOWMO = parseInt(process.env.PLAYWRIGHT_SLOWMO);
const { devices } = require('@playwright/test');
/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config: PlaywrightTestConfig = {
  testDir: `./tests/${TEST}`,
  testDir: '../browser-automated-tests-playwright',
  timeout: 180000,
  retries: 2,
  workers: 3,
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
    {
     name: 'Desktop Chromium',
      use: {
        browserName: 'chromium',
      },
    },
   //Test against mobile viewports.
   // {
   //   name: 'Mobile Safari',
   //   use: devices['iPhone 12'],
   // },
  ],
};

module.exports = config;
