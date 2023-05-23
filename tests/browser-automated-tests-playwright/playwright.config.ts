// playwright.config.js
// @ts-check
require('dotenv').config()
import { PlaywrightTestConfig } from '@playwright/test';
const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_SLOWMO = parseInt(process.env.PLAYWRIGHT_SLOWMO);
const { devices } = require('@playwright/test');
/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config: PlaywrightTestConfig = {
  testDir: 'tests',
  testDir: '../browser-automated-tests-playwright',
  timeout: 180000,
  retries: 1,
  workers: 1,
  fullyParallel: false,
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
  ],
};

module.exports = config;
