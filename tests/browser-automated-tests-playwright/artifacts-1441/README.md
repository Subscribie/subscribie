# Playwright artefacts for issue #1441

| File | What it shows |
| --- | --- |
| `01-subscribie-home.png` | Subscribie home page (proves the app was running when the spec ran). |
| `02-admin-route.png` | `/admin/dashboard` responds (redirects to login as expected when unauthenticated). |
| `03-email-none-name.png` | **The fix.** Rendered payment-failed email for the previously-crashing case (`subscriber_name = None`). Greeting degrades to `Hi ,` instead of throwing `AttributeError`. |
| `04-email-normal-name.png` | Control case — same template with a normal name — to demonstrate the happy path still works. |
| `demo-1441-fix.mp4` | Playwright recording of the spec run, covering all four screenshots above. |

Re-generate with:

```bash
cd tests/browser-automated-tests-playwright
PLAYWRIGHT_HOST=http://127.0.0.1:5000/ PLAYWRIGHT_HEADLESS=true \
  npx playwright test 1441_payment_failed_notification_fix.spec.js
```
