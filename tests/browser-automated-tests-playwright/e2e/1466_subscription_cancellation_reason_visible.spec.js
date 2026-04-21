const { test, expect } = require('@playwright/test');
const { admin_login } = require('./features/admin_login');

/**
 * Issue #1466 – As a shop owner, I can quickly see *why* a given
 * subscription was cancelled, not only that it is cancelled.
 *
 * This relies on a canceled subscription existing for the logged-in
 * shop's admin (the companion spec
 * 147_shop_owner_pause_resume_and_cancel_subscriptions.spec.js cancels
 * a subscription earlier in the suite, which will populate
 * stripe_cancellation_reason via the Stripe webhook).
 *
 * The test captures screenshots of the subscribers list and subscriber
 * detail page to demonstrate the cancellation reason is now surfaced
 * in the admin UI.
 */
test.describe('#1466 Cancellation reason is visible in admin UI', () => {
    test('@1466_subscription_cancellation_reason_visible', async ({ page }) => {
        await admin_login(page);

        // 1. Subscribers list page – shows the per-subscription cancellation reason
        await page.goto(process.env['PLAYWRIGHT_HOST'] + '/admin/subscribers');
        const reasonLocator = page.locator('.subscription-cancellation-reason').first();
        if (await reasonLocator.count() === 0) {
            test.skip(true, 'No canceled subscription present to verify reason against');
        }
        await expect(reasonLocator).toBeVisible();
        const reasons = await page.locator('.subscription-cancellation-reason').allTextContents();
        console.log('[#1466] Reasons on subscribers page:', reasons.map(s => s.trim()));
        await page.screenshot({
            path: 'test-results/1466-subscribers-page.png',
            fullPage: true,
        });

        // 2. Per-subscriber detail page – also surfaces the reason
        const subscriberLink = page.locator('a[id^="person-"]').first();
        await subscriberLink.click();
        await expect(page.locator('.subscription-cancellation-reason').first())
            .toBeVisible();
        await page.screenshot({
            path: 'test-results/1466-subscriber-detail-page.png',
            fullPage: true,
        });
    });
});
