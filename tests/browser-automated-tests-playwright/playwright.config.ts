import { defineConfig, devices } from '@playwright/test';
import YAML from 'yaml';
import fs from 'fs';
const path = require('path');

/**
 * Read the settings.yml configuration file.
 */

const settings_file = fs.readFileSync(path.resolve(__dirname, '../../settings.yaml'), 'utf8');

// Take each element from the YAML object and populate the process.env object.
const settings = YAML.parse(settings_file);
for (const key in settings) {
  console.log(`Setting ${key} to ${settings[key]} in process.env`);
  process.env[key] = settings[key];
}


const PLAYWRIGHT_HEADLESS = process.env.PLAYWRIGHT_HEADLESS.toLocaleLowerCase() == "true" || false;
const PLAYWRIGHT_HOST = process.env.PLAYWRIGHT_HOST;
const PLAYWRIGHT_SLOWMO = parseInt(process.env.PLAYWRIGHT_SLOWMO);

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 5 * 60 * 1000, // 5 minutes
  /* Run tests in files in parallel */
  fullyParallel: false,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : 1,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',

  preserveOutput: 'always',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    // baseURL: 'http://127.0.0.1:3000',

    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    baseURL: PLAYWRIGHT_HOST,
    headless: PLAYWRIGHT_HEADLESS,
    viewport: { width: 1280, height: 720 },
    launchOptions: {
      slowMo: PLAYWRIGHT_SLOWMO,

    },
    video: 'on',
    navigationTimeout: 1 * 60 * 1000, // 1 minutes, 
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
