// Playwright demo for issue #1441.
//
// Issue: https://github.com/Subscribie/subscribie/issues/1441
//
// The bug was in `subscribie/notifications.py` — a Stripe webhook with a null
// billing_details.name caused `subscriber_name.split(' ')` to raise
// AttributeError, so the subscriber never received the "your payment failed"
// email. This spec captures three visual artifacts that document the fix:
//
//   1. Subscribie is running (admin dashboard reachable).
//   2. The rendered payment-failed email for the previously-crashing case
//      (subscriber_name = None) — it now renders cleanly as "Hi ,".
//   3. The same template with a normal name, for before/after comparison.
//
// Runs with:
//   PLAYWRIGHT_HOST=http://127.0.0.1:5000/ PLAYWRIGHT_HEADLESS=true \
//     npx playwright test 1441_payment_failed_notification_fix.spec.js
//
// Output lands in ./artifacts-1441/ (gitignored) so the binaries are never
// committed. Attach them to the PR as comment uploads instead.
import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const ART_DIR = path.resolve(__dirname, '../artifacts-1441');
fs.mkdirSync(ART_DIR, { recursive: true });

test('issue #1441 fix — app is running and notification email renders with None subscriber_name', async ({ page }) => {
  // 1. Subscribie app is up
  await page.goto('/');
  await expect(page).toHaveTitle(/.+/);
  await page.screenshot({ path: path.join(ART_DIR, '01-subscribie-home.png'), fullPage: true });

  // 2. Admin area exists (redirects to login when not authenticated — that's
  //    fine; we just want to show the route responds).
  const adminResp = await page.goto('/admin/dashboard');
  expect(adminResp.status()).toBeLessThan(500);
  await page.screenshot({ path: path.join(ART_DIR, '02-admin-route.png'), fullPage: true });

  // 3. The rendered payment-failed email — None-name case.
  //    This is the exact HTML a subscriber would now receive when Stripe
  //    sends a webhook with billing_details.name = null. Before the fix,
  //    the notifier crashed and the email was never sent at all.
  await page.goto('file://' + path.resolve('/tmp/email-post-fix-none-name.html'));
  await expect(page.locator('body')).toContainText('payment collection failed');
  await page.screenshot({ path: path.join(ART_DIR, '03-email-none-name.png'), fullPage: true });

  // 4. Same template, normal name — control case.
  await page.goto('file://' + path.resolve('/tmp/email-post-fix-normal.html'));
  await expect(page.locator('body')).toContainText('Ada');
  await page.screenshot({ path: path.join(ART_DIR, '04-email-normal-name.png'), fullPage: true });

  // A small pause so the recorded video has a clear final frame on the email.
  await page.waitForTimeout(1000);
});
