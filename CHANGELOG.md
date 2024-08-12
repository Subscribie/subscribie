# v0.1.200 (Mon Aug 12 2024)

#### 🐛 Bug Fix

- #1390 only show date in person_created_at_date csv export [#1391](https://github.com/Subscribie/subscribie/pull/1391) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1390 person_created_at_date and person_created_at_time is included in CSV export [#1391](https://github.com/Subscribie/subscribie/pull/1391) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1390 black format [#1391](https://github.com/Subscribie/subscribie/pull/1391) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1390 show person.created_at in subscriber csv export [#1391](https://github.com/Subscribie/subscribie/pull/1391) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.199 (Sun Aug 11 2024)

#### 🐛 Bug Fix

- #1386 update playwright tests [#1389](https://github.com/Subscribie/subscribie/pull/1389) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1386 black format [#1389](https://github.com/Subscribie/subscribie/pull/1389) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1386 remove undeeded backfill_stripe_upcoming_invoices since they're updated in-place anyway [#1389](https://github.com/Subscribie/subscribie/pull/1389) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1386 add backfill endpoints and cli for backfill_transactions, backfill_subscriptions, backfill_persons and backfill_stripe_invoices [#1389](https://github.com/Subscribie/subscribie/pull/1389) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.198 (Sat Aug 10 2024)

#### 🐛 Bug Fix

- Fix #1387 create_at run at insertion time hotfix [#1388](https://github.com/Subscribie/subscribie/pull/1388) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.197 (Tue Jul 23 2024)

#### 🐛 Bug Fix

- Fix #1381 Include all question columns in CSV export [#1382](https://github.com/Subscribie/subscribie/pull/1382) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix: Dont attempt to create subscription if donation [#1380](https://github.com/Subscribie/subscribie/pull/1380) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1379 as a shop owner I see the subscriber name and email in new subscriber email notifications [#1380](https://github.com/Subscribie/subscribie/pull/1380) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.196 (Wed Jul 17 2024)

#### 🐛 Bug Fix

- 1376 as a shop owner i can view all invoices of a specific subscriber and refresh individual subscription statuses [#1378](https://github.com/Subscribie/subscribie/pull/1378) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.195 (Tue Jul 16 2024)

#### 🐛 Bug Fix

- #1376 black format [#1377](https://github.com/Subscribie/subscribie/pull/1377) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1376 As a shop owner, I can download invoices when I view an individual subscriber [#1377](https://github.com/Subscribie/subscribie/pull/1377) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.194 (Thu Jul 11 2024)

#### 🐛 Bug Fix

- Fix #1374 clear session chosen_question_ids_answers betweeen plan sign ups [#1375](https://github.com/Subscribie/subscribie/pull/1375) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.193 (Tue Jul 09 2024)

#### 🐛 Bug Fix

- #1368 black [#1372](https://github.com/Subscribie/subscribie/pull/1372) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1368 As a shop owner I can disable multicurrency support [#1372](https://github.com/Subscribie/subscribie/pull/1372) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.192 (Fri Jul 05 2024)

#### 🐛 Bug Fix

- #1370 add issue link for context [#1371](https://github.com/Subscribie/subscribie/pull/1371) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1370 graceful handling of webhook endpoint downtime [#1371](https://github.com/Subscribie/subscribie/pull/1371) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- WIP Fix #1370 Store note_to_seller regardless of if plan is a subscription or not [#1371](https://github.com/Subscribie/subscribie/pull/1371) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.191 (Sat Jun 29 2024)

#### 🐛 Bug Fix

- #1366 bump actions/checkout in action container-publish.yml [#1367](https://github.com/Subscribie/subscribie/pull/1367) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1366 bump actions/checkout & actions/setup-python in action python-package.yml [#1367](https://github.com/Subscribie/subscribie/pull/1367) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1366 announce-stripe-connect error handle endpoint downtime gracefully [#1367](https://github.com/Subscribie/subscribie/pull/1367) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.190 (Sun Jun 23 2024)

#### 🐛 Bug Fix

- Fix #1364 load plan share urls by plan name when uuid fallsback [#1365](https://github.com/Subscribie/subscribie/pull/1365) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.189 (Sat Jun 22 2024)

#### 🐛 Bug Fix

- Fix #1361 Preserve custom thank you email template if chosen [#1362](https://github.com/Subscribie/subscribie/pull/1362) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.188 (Fri Jun 21 2024)

#### 🐛 Bug Fix

- #1359 typo page slug [#1360](https://github.com/Subscribie/subscribie/pull/1360) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1359 Can mark questions as longform question as shopw owner [#1360](https://github.com/Subscribie/subscribie/pull/1360) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.187 (Sun Jun 09 2024)

#### 🐛 Bug Fix

- Fix #1357 fix verify prod onboarding workflow [#1358](https://github.com/Subscribie/subscribie/pull/1358) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.186 (Sun Jun 09 2024)

#### 🐛 Bug Fix

- Fix #1355 remove-pr-preview.yml by SUBDOMAIN [#1356](https://github.com/Subscribie/subscribie/pull/1356) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.185 (Fri Jun 07 2024)

#### 🐛 Bug Fix

- Fix #1353 dec2pence floating point precision [#1354](https://github.com/Subscribie/subscribie/pull/1354) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.184 (Wed Jun 05 2024)

#### ⚠️ Pushed to `master`

- Update release.yml ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.183 (Wed Jun 05 2024)

#### ⚠️ Pushed to `master`

- Update release.yml bump checkout to v4 ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.182 (Wed Jun 05 2024)

#### 🐛 Bug Fix

- Fix #1341 As shop owner, if my login expires, I'm redirected to previous page after re-authenticating [#1342](https://github.com/Subscribie/subscribie/pull/1342) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.181 (Wed Jun 05 2024)

:tada: This release contains work from a new contributor! :tada:

Thank you, null[@jimmyedagawa78](https://github.com/jimmyedagawa78), for all your work!

#### 🐛 Bug Fix

- Update release.yml #1347 [#1351](https://github.com/Subscribie/subscribie/pull/1351) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- 1347 as an operator the release workflow succeeds [#1350](https://github.com/Subscribie/subscribie/pull/1350) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1347 allow auto to run on protected branch [#1349](https://github.com/Subscribie/subscribie/pull/1349) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1345 Preserve questions attached to plans upon edit [#1346](https://github.com/Subscribie/subscribie/pull/1346) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1347 bump auto-it release workflow [#1348](https://github.com/Subscribie/subscribie/pull/1348) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Revert "Fix #1333 entrypoint listen on port 80 by default" [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 improve error_handler for 404s [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1333 entrypoint listen on port 80 by default [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 correct entrypoint debug output [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 black [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 tidy [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 black format [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 all tests passing [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1337 fix test private pages [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 fix test revert thankyou url verify [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1340 check subscribie_checkout_session_id over stripe_subscription_id to account for free plans [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 e2e/1219_custom_thank_you_url.spec.js [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 update default datetime to use datetime.UTC [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 default subscription answers to empty list [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 update testing docs SUBSCRIBER_EMAIL_USER [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1339 AttributeError: 'BabelConfiguration' object has no attribute 'domain_instance'' [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 drop breakpoint [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 seed.sql remove builder module [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 black format migrations [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 format black [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1336 include build tools Dockerfile [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #1336 Fix tests [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- format tests/conftest.py [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1336 Fix pytest tests [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- WIP Fix #1336 simply stop unlinking the database prematurely TODO test only unlink removal [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- WIP #1333 add missing null migration [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip Fix #1333 Forms Questions during plan sign up [#1335](https://github.com/Subscribie/subscribie/pull/1335) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1330 cancellations page Person .one -> .one_or_none [#1332](https://github.com/Subscribie/subscribie/pull/1332) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1330 ignore archived subscribers when showing Recent Subscription Cancellations [#1331](https://github.com/Subscribie/subscribie/pull/1331) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1328 Disable refresh subscribers button after pressed [#1329](https://github.com/Subscribie/subscribie/pull/1329) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1307 faster subscription status refreshes 30 days default [#1327](https://github.com/Subscribie/subscribie/pull/1327) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix 1324 check subscription.note is not None before adding to subscription cancelation email [#1325](https://github.com/Subscribie/subscribie/pull/1325) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1321 demo shop link to exampleshop.subscriby.shop [#1322](https://github.com/Subscribie/subscribie/pull/1322) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1319 When showing subscriber failed invoices, don't check decline code of paid invoices [#1320](https://github.com/Subscribie/subscribie/pull/1320) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1317 As a subscriber I can't see old archived plans which don't have a pricelist attached [#1318](https://github.com/Subscribie/subscribie/pull/1318) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1315 ensure trial_period_days default to 0 when None [#1316](https://github.com/Subscribie/subscribie/pull/1316) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1313 PR template typos [#1314](https://github.com/Subscribie/subscribie/pull/1314) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1311 flake8/black tidy [#1312](https://github.com/Subscribie/subscribie/pull/1312) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1308 if a subscription is cancelled by the lack of payments send shop owner notification [#1310](https://github.com/Subscribie/subscribie/pull/1310) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1308 when a subscription is cancelled, email the shop owner with context [#1309](https://github.com/Subscribie/subscribie/pull/1309) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1305 when plan archived, its new plan has pointer to prior revision on plan.parent_plan_revision_uuid [#1306](https://github.com/Subscribie/subscribie/pull/1306) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1301 use of colour to differentiate subscription statuses on subscriber list page [#1302](https://github.com/Subscribie/subscribie/pull/1302) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1294 Show subscripton ended_at (cancelled at) date on subscribers list if subscription has ended [#1300](https://github.com/Subscribie/subscribie/pull/1300) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1295 remove auto_paging_iter from stats.py for recent cancellations [#1299](https://github.com/Subscribie/subscribie/pull/1299) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Ref #1295 remove Events auto_paging_iter as auto pager appears to be duplicating returned events [#1298](https://github.com/Subscribie/subscribie/pull/1298) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch '1295-as-a-shop-owner-when-i-log-into-my-dashboard-i-see-a-list-of' of github.com:Subscribie/subscribie into 1295-as-a-shop-owner-when-i-log-into-my-dashboard-i-see-a-list-of [#1297](https://github.com/Subscribie/subscribie/pull/1297) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1295 show customer balanse alongside recent cancellations [#1296](https://github.com/Subscribie/subscribie/pull/1296) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1295 remove unused code from recent_subscription_cancellations.html [#1296](https://github.com/Subscribie/subscribie/pull/1296) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1295 As a shop owner, I can see a list of recently cancelled subscriptions via the dashboard [#1296](https://github.com/Subscribie/subscribie/pull/1296) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1292 verify transaction.subscription.note is str before strip [#1293](https://github.com/Subscribie/subscribie/pull/1293) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1290 refresh invocie cache on every payment_intent.succeeded event [#1291](https://github.com/Subscribie/subscribie/pull/1291) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1288 admin/refresh-invoices background thread with app context [#1289](https://github.com/Subscribie/subscribie/pull/1289) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1285 get EMAIL_QUEUE_FOLDER from settings not os env [#1286](https://github.com/Subscribie/subscribie/pull/1286) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1283 correctly escape plan descriptions [#1284](https://github.com/Subscribie/subscribie/pull/1284) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch '773-outstanding-payments' into 1276-upgrade-to-python-312-use-rye [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1282 Stats to include archived plans [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1282 include archived plans in calculating active subscribers [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 python min version 3.12 [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- tidy [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 bump minimal python version [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- downgrade stripe_api_key not set to a warning [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Ref #1276 remove MAIN_SERVER setting [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 update .envsubst.template for subscribie deployer [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 use importlib.resources for datafiles import [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 load seed.sql from package if not found in cwd [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 get theme and static folders from package if configured does not exist [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 calculate migrations directory using pathlib/__file__ so migratinos work after python packaging [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 remove unused packages python-dotenv, update .gitignore [#1279](https://github.com/Subscribie/subscribie/pull/1279) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Wip Fix #1039 use strictyaml for app settings [#1040](https://github.com/Subscribie/subscribie/pull/1040) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch '1276-upgrade-to-python-312-use-rye' of github.com:Subscribie/subscribie into 1276-upgrade-to-python-312-use-rye [#1040](https://github.com/Subscribie/subscribie/pull/1040) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1276 set vassal virtualenv venv path to .venv (rye default) [#1040](https://github.com/Subscribie/subscribie/pull/1040) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #1276 upgrade markupsafe, remove before_app_first_request usage, MAX_CONTEXT_LENGTH update [#1040](https://github.com/Subscribie/subscribie/pull/1040) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip Fix #1276 use python 3.12 using rye & update all packages [#1040](https://github.com/Subscribie/subscribie/pull/1040) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1277 remove hardcoded subscriby.shop, use SUBSCRIBIE_DOMAIN [#1278](https://github.com/Subscribie/subscribie/pull/1278) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #773 Easily see failed payments per subscriber [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #773 wip show subscriber balance/missed payments [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #773 On show-subscriber "Subscriber Balance" is now shown [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #773 tidy wip customer balance [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch '773-outstanding-payments' of github.com:Subscribie/subscribie into 773-outstanding-payments [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- contxt dependent header for outstanding payments dashboard/transactions [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@elliottmotson](https://github.com/elliottmotson))
- def getpaymentissues() skeleton function to fech outstanding payments [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@elliottmotson](https://github.com/elliottmotson))
- Switched to bs cards, jinja2 for card formatting and colour grading [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@elliottmotson](https://github.com/elliottmotson))
- Reformatted placeholder vars, introduced "customer" dict, UX improvement [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@elliottmotson](https://github.com/elliottmotson))
- introduced currencyFilter into issues.html [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@elliottmotson](https://github.com/elliottmotson))
- issues.html, init.py has /issues, outstanding_payments func hardcoded [#1275](https://github.com/Subscribie/subscribie/pull/1275) ([@elliottmotson](https://github.com/elliottmotson))
- #1219 redirect thank you page url [#1232](https://github.com/Subscribie/subscribie/pull/1232) ([@jimmyedagawa78](https://github.com/jimmyedagawa78) [@joeltejeda](https://github.com/joeltejeda) [@chrisjsimpson](https://github.com/chrisjsimpson))
- removing cancel_at test [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- changing video folder name [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- adding video folder, updating demo-video workflow [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- adding video path [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- removing test [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- removing one test [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- checking back to default core [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- removing test 623_subscriber_magic_login_and_reset_password [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- adding test back [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- announcing shop [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- removing some test [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- updating workflow playwright version [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- updating test file [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- formatting with black [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- updating tests [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- adding parallel test to workflow [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- adding new tests requirements [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- test [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- #1048 test ensure terms & conditions is assigned. Use setChecked(true) [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- updating tests dependencies and adding clead_db tests [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@joeltejeda](https://github.com/joeltejeda))
- wip #1048 update testing.md documentation [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1048 renamed: PW.py -> run-playwright-tests.py [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Ref #1048 git ignore screenshots, drop unused tests (todo restore) [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1048 show test name currently running during test runs ref 43b7bbdf95e67aa71d6a6d2afc0ed7a2f4f2a3ee [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Ref #1048 always save latest tax rate ref #463 [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1048 add route set_test_name cookie for +@development_mode_only [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1048 default timeout to 5 minutes [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Ref #1048 refactor tests [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #1048 playwright refactor based on https://github.com/KarmaComputing/dag-directed-acyclic-graph-example/tree/playwright [#1164](https://github.com/Subscribie/subscribie/pull/1164) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- show time saving calculator rather than revenue calculator [#1247](https://github.com/Subscribie/subscribie/pull/1247) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1238 regression: as subscriber I can see my subscriptions [#1239](https://github.com/Subscribie/subscribie/pull/1239) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1243 caseinsensitive subscriber login [#1244](https://github.com/Subscribie/subscribie/pull/1244) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Revert "changing to lowercase database output email" [#1241](https://github.com/Subscribie/subscribie/pull/1241) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- changing to lowercase database output email [#1235](https://github.com/Subscribie/subscribie/pull/1235) ([@joeltejeda](https://github.com/joeltejeda))
- adding lower case to email [#1234](https://github.com/Subscribie/subscribie/pull/1234) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1228 all shop admins notified of payment_intent.payment_failed [#1229](https://github.com/Subscribie/subscribie/pull/1229) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- 1207 as operator pr previews older than x daysperiod are automati [#1231](https://github.com/Subscribie/subscribie/pull/1231) ([@chrisjsimpson](https://github.com/chrisjsimpson) [@joeltejeda](https://github.com/joeltejeda))
- 1207 as operator pr previews older than x daysperiod are automati [#1230](https://github.com/Subscribie/subscribie/pull/1230) ([@chrisjsimpson](https://github.com/chrisjsimpson) [@joeltejeda](https://github.com/joeltejeda))
- 1207 as operator pr previews older than x daysperiod are automati [#1216](https://github.com/Subscribie/subscribie/pull/1216) ([@chrisjsimpson](https://github.com/chrisjsimpson) [@joeltejeda](https://github.com/joeltejeda))
- Fix #1221 don't assume subscriptions have a note' [#1223](https://github.com/Subscribie/subscribie/pull/1223) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1212 show customer note on csv transactions export [#1213](https://github.com/Subscribie/subscribie/pull/1213) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #1212 csv export consistent naming Donation -> is_donation [#1213](https://github.com/Subscribie/subscribie/pull/1213) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1207 black formatted countryToCurrency which bypassed protections test [#1211](https://github.com/Subscribie/subscribie/pull/1211) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding support for BRL and Brazil [#1209](https://github.com/Subscribie/subscribie/pull/1209) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- #1204 added missing macro plan_card.html [#1205](https://github.com/Subscribie/subscribie/pull/1205) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1204 add plan_card macro for choose.html in ./themes/theme-jesmond/jesmon/macros [#1205](https://github.com/Subscribie/subscribie/pull/1205) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Create documentation for failed payments [#1198](https://github.com/Subscribie/subscribie/pull/1198) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- update translation in spanish [#1187](https://github.com/Subscribie/subscribie/pull/1187) ([@joeltejeda](https://github.com/joeltejeda))
- #1014 spacing around contextual refresh button [#1187](https://github.com/Subscribie/subscribie/pull/1187) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1014 update translations for French and German [#1187](https://github.com/Subscribie/subscribie/pull/1187) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1014 provide contextual button to refresh subscriptions if delay in processing rather than asking user to go elsewhere [#1187](https://github.com/Subscribie/subscribie/pull/1187) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1014 close unclosed tags [#1187](https://github.com/Subscribie/subscribie/pull/1187) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- FIX #1014 adding a message if there are no plans attached [#1187](https://github.com/Subscribie/subscribie/pull/1187) ([@joeltejeda](https://github.com/joeltejeda))
- refactoring the curl command and adding the badge to the README [#1192](https://github.com/Subscribie/subscribie/pull/1192) ([@joeltejeda](https://github.com/joeltejeda))
- Created a Blog status checker [#1191](https://github.com/Subscribie/subscribie/pull/1191) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- adding video guides to docs [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- updating and optimising docs [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- updating docs with thumbnails [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- adding thumbnails to docs [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Adding links and youtube guides to docs [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Adding new docs for adding a free trial and adding a logo, adding additional context links and youtube tutorials [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- #1171 explain how documents work from a subscribers perspective, and link to file uploads also [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1171 renamed: add-documents-to-plans -> add-documents-to-plans.md [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- renaming customising email guide and spelling [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- adding guides to subscribie docs [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Create add-documents-to-plans [#1172](https://github.com/Subscribie/subscribie/pull/1172) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- updating Dockerfile [#1127](https://github.com/Subscribie/subscribie/pull/1127) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1126 anti-spam shopname route http://127.0.0.1:5000/admin/spamcheck/ [#1127](https://github.com/Subscribie/subscribie/pull/1127) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip Fix #1126 detect spam shops ml [#1127](https://github.com/Subscribie/subscribie/pull/1127) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1126 black format run.py [#1127](https://github.com/Subscribie/subscribie/pull/1127) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1126 anti-spam shopname route http://127.0.0.1:5000/admin/spamcheck/ [#1127](https://github.com/Subscribie/subscribie/pull/1127) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- ignoring release github action when documents are being edited [#1177](https://github.com/Subscribie/subscribie/pull/1177) ([@joeltejeda](https://github.com/joeltejeda))
- fixing open shortcode in index file [#1175](https://github.com/Subscribie/subscribie/pull/1175) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Fix #1161 use SUBDOMAIN over github.head_ref for pr-preview [#1163](https://github.com/Subscribie/subscribie/pull/1163) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding the missing env. next to subdomain [#1162](https://github.com/Subscribie/subscribie/pull/1162) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1161 changing head-ref with SUBDOMAIN [#1162](https://github.com/Subscribie/subscribie/pull/1162) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1159 ensure appname pr preview last character is always alphanumeric [#1160](https://github.com/Subscribie/subscribie/pull/1160) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #Fix 1151 set remove-pr-preview.yml to testing environment [#1152](https://github.com/Subscribie/subscribie/pull/1152) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1148 enable donations link fix [#1155](https://github.com/Subscribie/subscribie/pull/1155) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Updating Docs Format [#1155](https://github.com/Subscribie/subscribie/pull/1155) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Added language list [#1131](https://github.com/Subscribie/subscribie/pull/1131) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Updated multi-language support answer [#1131](https://github.com/Subscribie/subscribie/pull/1131) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- adding multi-language support to FAQ [#1131](https://github.com/Subscribie/subscribie/pull/1131) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Update add-team-members.md title [#1145](https://github.com/Subscribie/subscribie/pull/1145) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- #1117 clarify how to do payment refunds [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1117 clarify csv export subscribers [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1117 clarify email reply-to [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1117 cooling off period vs free trial period [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- updated docs with proper markdown [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- #1117 correct working on change shop name [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1117 clarify wording on collecting order notes [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding more guides to docs [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Ad-hoc charge guide [#1121](https://github.com/Subscribie/subscribie/pull/1121) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- #1122 tidy migration merge [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1122 merge migrations hasreadonly with has_sell_price_min merge [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Revert "wip #1122 adding the login to get the subscribers agreed terms of service" [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #1122 adding the login to get the subscribers agreed terms of service [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@joeltejeda](https://github.com/joeltejeda))
- wip #1122 adding the login to get the subscribers agreed terms of service [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1122 when showing terms-and-conditions-agreed also filter by read_only [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Ref #1122 when showing terms-and-conditions-agreed also filter by read_only [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1122 correct working, subscriptions canot presently be archived so dont suggest they can be [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1122 add @development_mode_only decorator [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding a remove-documents call to fix the error of no documents attached to plans [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1112 mark subscription document(s) as read_only during sign-up [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip Fix #1112 add HasReadOnly read_only to Document model [#1139](https://github.com/Subscribie/subscribie/pull/1139) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1146 update runner from ubuntu-20.04 to ubuntu-22.04 [#1147](https://github.com/Subscribie/subscribie/pull/1147) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1032 black format [#1143](https://github.com/Subscribie/subscribie/pull/1143) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1032 black format 5259c05704c4_merge_has_min_sell_price_has_min_.py [#1143](https://github.com/Subscribie/subscribie/pull/1143) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1032 db migrations merge has_min_sell_price has_min_interval_amount with is_donation 262c26af9630 94790e701430 [#1143](https://github.com/Subscribie/subscribie/pull/1143) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1032 added test test_create_PriceList_and_price_list_rule_percent_discount [#1143](https://github.com/Subscribie/subscribie/pull/1143) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1032 use has_min_sell_price has_min_interval during PriceRule calculation [#1143](https://github.com/Subscribie/subscribie/pull/1143) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #1079 donation email sending [#1097](https://github.com/Subscribie/subscribie/pull/1097) ([@joeltejeda](https://github.com/joeltejeda) [@chrisjsimpson](https://github.com/chrisjsimpson))
- #1141 fix include archived plans when listing agreed to documents on /admin/list-documents?filter=terms-and-conditions-agreed [#1142](https://github.com/Subscribie/subscribie/pull/1142) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1135 set doc agreed if of type otherwise keep the type of the document [#1138](https://github.com/Subscribie/subscribie/pull/1138) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1135 updating the logic of agreed terms and conditions documents [#1138](https://github.com/Subscribie/subscribie/pull/1138) ([@joeltejeda](https://github.com/joeltejeda))
- [docs] Document how to add database migrations ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding screenshots and video to the new UI [#1120](https://github.com/Subscribie/subscribie/pull/1120) ([@joeltejeda](https://github.com/joeltejeda))
- Added Malaysia & Mexico Support [#1118](https://github.com/Subscribie/subscribie/pull/1118) ([@jimmyedagawa78](https://github.com/jimmyedagawa78) [@joeltejeda](https://github.com/joeltejeda))
- 1124 - added countries support to FAQ [#1125](https://github.com/Subscribie/subscribie/pull/1125) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Fix #1105 show num_donations not total_donations [#1107](https://github.com/Subscribie/subscribie/pull/1107) ([@chrisjsimpson](https://github.com/chrisjsimpson) [@joeltejeda](https://github.com/joeltejeda))
- filtering the dasboard to the corresponding groups [#1108](https://github.com/Subscribie/subscribie/pull/1108) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1106 filtering donations and refunds in transactions [#1109](https://github.com/Subscribie/subscribie/pull/1109) ([@joeltejeda](https://github.com/joeltejeda))
- #1112 preserve selected language choice in footer [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1112 hrvatska -> Hrvatski language not country name [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1112 padding to footer for language selection [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1112 add missing fr to LANGUAGES [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1112 dont assume language_code in session & add logging [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding the support language in session [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@joeltejeda](https://github.com/joeltejeda))
- wip Language selection Fix #1112 [#1114](https://github.com/Subscribie/subscribie/pull/1114) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip Fix #1110 add French translation [#1111](https://github.com/Subscribie/subscribie/pull/1111) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding comments to the line [#1104](https://github.com/Subscribie/subscribie/pull/1104) ([@joeltejeda](https://github.com/joeltejeda))
- 1095 fix donations checkout [#1096](https://github.com/Subscribie/subscribie/pull/1096) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1101 donation test comments [#1102](https://github.com/Subscribie/subscribie/pull/1102) ([@joeltejeda](https://github.com/joeltejeda))
- 1098 xss fix for plan titles [#1099](https://github.com/Subscribie/subscribie/pull/1099) ([@joeltejeda](https://github.com/joeltejeda))
- 1055 fixing rename shop feature [#1094](https://github.com/Subscribie/subscribie/pull/1094) ([@joeltejeda](https://github.com/joeltejeda))
- 1070 fix shop owner magic login [#1093](https://github.com/Subscribie/subscribie/pull/1093) ([@joeltejeda](https://github.com/joeltejeda))
- 1088 export donations transactions [#1092](https://github.com/Subscribie/subscribie/pull/1092) ([@joeltejeda](https://github.com/joeltejeda))
- 1089 docs how to add donations [#1091](https://github.com/Subscribie/subscribie/pull/1091) ([@joeltejeda](https://github.com/joeltejeda))
- added docs for donations and viewing transactions [#1090](https://github.com/Subscribie/subscribie/pull/1090) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- add croatian language [#1085](https://github.com/Subscribie/subscribie/pull/1085) ([@joeltejeda](https://github.com/joeltejeda))
- 1082 verify prod onboarding timeout [#1083](https://github.com/Subscribie/subscribie/pull/1083) ([@joeltejeda](https://github.com/joeltejeda))
- 1065 donations feature tests [#1080](https://github.com/Subscribie/subscribie/pull/1080) ([@joeltejeda](https://github.com/joeltejeda))
- 1071 force email address lowercase [#1075](https://github.com/Subscribie/subscribie/pull/1075) ([@joeltejeda](https://github.com/joeltejeda))
- 1065 donation pot [#1066](https://github.com/Subscribie/subscribie/pull/1066) ([@joeltejeda](https://github.com/joeltejeda) [@jimmyedagawa78](https://github.com/jimmyedagawa78) [@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1077 dont try to access plan if none [#1078](https://github.com/Subscribie/subscribie/pull/1078) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1073 show interval_unit on /admin/subscribers [#1074](https://github.com/Subscribie/subscribie/pull/1074) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Update why-subscribie.html ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Added Windows instruction [#1069](https://github.com/Subscribie/subscribie/pull/1069) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- 1060 removing selling points required [#1061](https://github.com/Subscribie/subscribie/pull/1061) ([@joeltejeda](https://github.com/joeltejeda))

#### ⚠️ Pushed to `master`

- Update release.yml ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 questions with options required ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1333 add missing question templates ([@chrisjsimpson](https://github.com/chrisjsimpson))
- remove breakpoint ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch 'master' of github.com:Subscribie/subscribie ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1282 include archived plans in calculating active subscribers ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding pr preview badge ([@joeltejeda](https://github.com/joeltejeda))
- removing a space from the README ([@joeltejeda](https://github.com/joeltejeda))
- improve landing page support and testimonals ([@chrisjsimpson](https://github.com/chrisjsimpson))
- auto create issue branches ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #1100 not adding the total_donations if the donation has been refunded ([@joeltejeda](https://github.com/joeltejeda))
- reverting back line 8 ([@joeltejeda](https://github.com/joeltejeda))
- Fix #1072 zoom in on plan when hover ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### 🔩 Dependency Updates

- Bump requests from 2.27.1 to 2.31.0 [#1166](https://github.com/Subscribie/subscribie/pull/1166) ([@dependabot[bot]](https://github.com/dependabot[bot]))

#### Authors: 5

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@dependabot[bot]](https://github.com/dependabot[bot])
- [@jimmyedagawa78](https://github.com/jimmyedagawa78)
- [@joeltejeda](https://github.com/joeltejeda)
- Elliott Sabin-Motson ([@elliottmotson](https://github.com/elliottmotson))

---

# v0.1.180 (Wed Feb 08 2023)

#### 🐛 Bug Fix

- 1057 spanish translation [#1062](https://github.com/Subscribie/subscribie/pull/1062) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.179 (Tue Feb 07 2023)

#### 🐛 Bug Fix

- 1058 improve auth logging [#1059](https://github.com/Subscribie/subscribie/pull/1059) ([@chrisjsimpson](https://github.com/chrisjsimpson) [@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.178 (Tue Feb 07 2023)

#### 🐛 Bug Fix

- 1063 sqlalchemy fix version [#1064](https://github.com/Subscribie/subscribie/pull/1064) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.177 (Sun Jan 29 2023)

#### 🐛 Bug Fix

- Fix #1035 add /notification test endpoint [#1036](https://github.com/Subscribie/subscribie/pull/1036) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #1037 log stripe onboarding errors dont return [#1038](https://github.com/Subscribie/subscribie/pull/1038) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.176 (Sun Jan 29 2023)

#### ⚠️ Pushed to `master`

- Ref #1054 re-compile translations de ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.175 (Sun Jan 29 2023)

#### 🐛 Bug Fix

- Fix #1054 additional help logging into shops docs [#1056](https://github.com/Subscribie/subscribie/pull/1056) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.174 (Tue Jan 24 2023)

#### 🐛 Bug Fix

- Fix #1052 provide link to help login [#1053](https://github.com/Subscribie/subscribie/pull/1053) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.173 (Thu Jan 12 2023)

#### 🐛 Bug Fix

- Update demo videos [#1047](https://github.com/Subscribie/subscribie/pull/1047) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.172 (Thu Jan 12 2023)

#### 🐛 Bug Fix

- Test pr preview master [#1046](https://github.com/Subscribie/subscribie/pull/1046) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.171 (Thu Jan 12 2023)

#### 🐛 Bug Fix

- 1041 fixing pr deploy [#1042](https://github.com/Subscribie/subscribie/pull/1042) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.170 (Sat Dec 24 2022)

#### 🐛 Bug Fix

- fix #1024 added new zealand support with usd [#1025](https://github.com/Subscribie/subscribie/pull/1025) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.169 (Sat Dec 17 2022)

#### 🐛 Bug Fix

- Fix #1028 set session expiration 30mins [#1029](https://github.com/Subscribie/subscribie/pull/1029) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.168 (Thu Dec 15 2022)

#### 🐛 Bug Fix

- 1022 australia support with usd [#1023](https://github.com/Subscribie/subscribie/pull/1023) ([@joeltejeda](https://github.com/joeltejeda))
- Added canada to currency [#1019](https://github.com/Subscribie/subscribie/pull/1019) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 2

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.167 (Mon Nov 28 2022)

#### ⚠️ Pushed to `master`

- added task for adding team members and TnC ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.166 (Fri Nov 25 2022)

#### ⚠️ Pushed to `master`

- proofing tasks ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.165 (Thu Nov 24 2022)

#### 🐛 Bug Fix

- 1005 terms and conditions subscriber [#1013](https://github.com/Subscribie/subscribie/pull/1013) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.164 (Wed Nov 23 2022)

#### 🐛 Bug Fix

- adding subscriber view test of terms and conditions [#1012](https://github.com/Subscribie/subscribie/pull/1012) ([@joeltejeda](https://github.com/joeltejeda))
- adding playwright test termns and condition creation and checkout [#1012](https://github.com/Subscribie/subscribie/pull/1012) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.163 (Wed Nov 23 2022)

#### ⚠️ Pushed to `master`

- adjust tasts ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.162 (Tue Nov 22 2022)

#### 🐛 Bug Fix

- Merge branch 'master' of github.com:Subscribie/subscribie into 1005-terms-and-conditions [#1006](https://github.com/Subscribie/subscribie/pull/1006) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.161 (Tue Nov 22 2022)

#### 🐛 Bug Fix

- #194 undo hardcode de locale [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- more #194 de translation new_customer plan.showItervalUnit() [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #194 de translation new_customer plan.showItervalUnit [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding missing quotes to the choose template [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- #194 enable gettext via flask_babel helpers to inject gettext functions after enabling the i18n extention for private pages [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #194 wip enable i18n translation for custom loaded pages [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- updating the translation file [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translation layout template for subscribers to de and adding a new layout just for the subscriber side [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating subscriber_failed_invoices, subscriptions and update_choices templates to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating subscriber list_files, reset_password and login templates to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translation subscribers account and forgot password templates to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- reverting back the template of the admin dashboard [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translate connect google tag manager and connect tawk manually to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating change email and password templates to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating add shop admin and cancel subscription templates to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating add custome code and add plan templates to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- fixing 404 html translation [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating 404 and 500 errors to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- fixing transaltion mispelled [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating order_summary and thankyou page to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating new_customer to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating set_options and view-plan to DE [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- translating choose theme jesmod to de [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- adding german languange to layout jesmond theme [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@joeltejeda](https://github.com/joeltejeda))
- #194 choose german translation [#1004](https://github.com/Subscribie/subscribie/pull/1004) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.160 (Tue Nov 22 2022)

#### 🐛 Bug Fix

- #990 remove example docs and improve Dashboard overview page [#1011](https://github.com/Subscribie/subscribie/pull/1011) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.159 (Sun Nov 20 2022)

#### 🐛 Bug Fix

- partial revert 7320b43a1da1c478c109d339355b42932e3545ee #935 [#992](https://github.com/Subscribie/subscribie/pull/992) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.158 (Fri Nov 18 2022)

#### ⚠️ Pushed to `master`

- adding guides ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.157 (Thu Nov 17 2022)

#### 🐛 Bug Fix

- Revert "Fix #1007 tuple as no object status code" [#1010](https://github.com/Subscribie/subscribie/pull/1010) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.156 (Thu Nov 17 2022)

#### 🐛 Bug Fix

- Fix #1007 tuple as no object status code [#1008](https://github.com/Subscribie/subscribie/pull/1008) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.155 (Thu Nov 17 2022)

#### 🐛 Bug Fix

- document translation how to [#1002](https://github.com/Subscribie/subscribie/pull/1002) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip Fix #194 translation support multilingual [#1002](https://github.com/Subscribie/subscribie/pull/1002) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### ⚠️ Pushed to `master`

- adding tasks for creation of pages, files, slogans, colours and pausing subscribers ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.154 (Wed Nov 16 2022)

#### 🐛 Bug Fix

- Fix #1000 correcting the baseurl in the config toml [#1001](https://github.com/Subscribie/subscribie/pull/1001) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.153 (Wed Nov 16 2022)

#### ⚠️ Pushed to `master`

- adding guides and moving to existing guides to tasks ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.152 (Tue Nov 15 2022)

#### ⚠️ Pushed to `master`

- adding tutorials ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.151 (Fri Nov 11 2022)

#### 🐛 Bug Fix

- Update shop-owners-updating-credit-card-details.md [#994](https://github.com/Subscribie/subscribie/pull/994) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Update shop-owners-updating-credit-card-details.md [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- updating template [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- adding update credit card details docs [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- #993 use SAAS_URL from env -> saas_url in template not hard code url [#994](https://github.com/Subscribie/subscribie/pull/994) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- declaring a constant [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- updaing node version and package.json update [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- updating playwright version [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- adding change card details test [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- changing the name of the card details test [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- #993 adding nav bar button on builder theme and link on jesmond dashboard [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #993 adding const to variables and playwright test to changing cards details [#994](https://github.com/Subscribie/subscribie/pull/994) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.150 (Fri Nov 11 2022)

#### ⚠️ Pushed to `master`

- adding guides for reordering plans, signup test and subscription and stripe creation ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.149 (Thu Nov 10 2022)

#### ⚠️ Pushed to `master`

- update docs demonstrate which pipelines run again ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.148 (Thu Nov 10 2022)

#### ⚠️ Pushed to `master`

- added tutorial for create private pages ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.147 (Thu Nov 10 2022)

#### ⚠️ Pushed to `master`

- add plan description tutorial ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.146 (Thu Nov 10 2022)

#### 🐛 Bug Fix

- fixing smoketest [#999](https://github.com/Subscribie/subscribie/pull/999) ([@joeltejeda](https://github.com/joeltejeda))
- getting the files inside the public folder not the folder [#999](https://github.com/Subscribie/subscribie/pull/999) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.145 (Thu Nov 10 2022)

#### 🐛 Bug Fix

- #990 smoketest docs at end [#998](https://github.com/Subscribie/subscribie/pull/998) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.144 (Thu Nov 10 2022)

#### 🐛 Bug Fix

- #990 chmod +x smoketest-docs.sh [#997](https://github.com/Subscribie/subscribie/pull/997) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.143 (Thu Nov 10 2022)

#### 🐛 Bug Fix

- removing folder instead of files [#996](https://github.com/Subscribie/subscribie/pull/996) ([@joeltejeda](https://github.com/joeltejeda) [@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.142 (Wed Nov 09 2022)

#### 🐛 Bug Fix

- #990 wip hugo docs [#991](https://github.com/Subscribie/subscribie/pull/991) ([@chrisjsimpson](https://github.com/chrisjsimpson) [@joeltejeda](https://github.com/joeltejeda) [@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 3

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@jimmyedagawa78](https://github.com/jimmyedagawa78)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.141 (Sun Nov 06 2022)

#### 🐛 Bug Fix

- Fix #988 fix next_payment_attempt removed by mistake [#989](https://github.com/Subscribie/subscribie/pull/989) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.140 (Sun Nov 06 2022)

#### 🐛 Bug Fix

- Fix #982 matching stripe livemode with the event stripelivemode [#983](https://github.com/Subscribie/subscribie/pull/983) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.139 (Sat Nov 05 2022)

#### 🐛 Bug Fix

- Fix #986 refactor events & signals [#987](https://github.com/Subscribie/subscribie/pull/987) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.138 (Sat Oct 29 2022)

#### 🐛 Bug Fix

- #980 lowercase checkshopname exists [#984](https://github.com/Subscribie/subscribie/pull/984) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch '980-api-check-shopname-exists' of github.com:Subscribie/subscribie into 980-api-check-shopname-exists [#984](https://github.com/Subscribie/subscribie/pull/984) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #980 restore change to api_get_magic_login_link made in error [#981](https://github.com/Subscribie/subscribie/pull/981) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #980 add api call /api/shop-name-taken/ lookup [#981](https://github.com/Subscribie/subscribie/pull/981) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### ⚠️ Pushed to `master`

- #980 remove spaced when checking shopname taken ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Merge branch 'master' of github.com:Subscribie/subscribie into 980-api-check-shopname-exists ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.137 (Sat Oct 29 2022)

#### 🐛 Bug Fix

- #980 lowercase checkshopname exists [#984](https://github.com/Subscribie/subscribie/pull/984) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #980 restore change to api_get_magic_login_link made in error [#984](https://github.com/Subscribie/subscribie/pull/984) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #980 add api call /api/shop-name-taken/ lookup [#984](https://github.com/Subscribie/subscribie/pull/984) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.136 (Thu Oct 27 2022)

#### 🐛 Bug Fix

- #980 restore change to api_get_magic_login_link made in error [#981](https://github.com/Subscribie/subscribie/pull/981) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #980 add api call /api/shop-name-taken/ lookup [#981](https://github.com/Subscribie/subscribie/pull/981) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.135 (Wed Oct 26 2022)

#### 🐛 Bug Fix

- Fix #935 removing dead code [#978](https://github.com/Subscribie/subscribie/pull/978) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.134 (Mon Oct 17 2022)

#### 🐛 Bug Fix

- Fix #976 update send email workflow adding IMAP_SEARCH_UNSEEN variable [#977](https://github.com/Subscribie/subscribie/pull/977) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.133 (Mon Oct 17 2022)

#### 🐛 Bug Fix

- updating seed sql for test site [#975](https://github.com/Subscribie/subscribie/pull/975) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #974 removing multi-currency migration code [#975](https://github.com/Subscribie/subscribie/pull/975) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.132 (Sat Oct 15 2022)

#### ⚠️ Pushed to `master`

- Added subscribie-intro-video.mp4 to README.md ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.131 (Sat Oct 15 2022)

#### ⚠️ Pushed to `master`

- Page -> page on choose.html ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.130 (Sat Oct 15 2022)

#### ⚠️ Pushed to `master`

- moneyback -> money-back. UP ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.129 (Sat Oct 15 2022)

#### 🐛 Bug Fix

- Fix #972 show video on homepage builder theme [#973](https://github.com/Subscribie/subscribie/pull/973) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.128 (Sat Oct 15 2022)

#### 🐛 Bug Fix

- adding more comments to the backward compatibility code [#971](https://github.com/Subscribie/subscribie/pull/971) ([@joeltejeda](https://github.com/joeltejeda))
- adding backwards compability for existing shops [#971](https://github.com/Subscribie/subscribie/pull/971) ([@joeltejeda](https://github.com/joeltejeda))
- reverting changes [#971](https://github.com/Subscribie/subscribie/pull/971) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.127 (Fri Oct 14 2022)

#### 🐛 Bug Fix

- Fix #969 join subscription and plan table for interval amount and sell price [#970](https://github.com/Subscribie/subscribie/pull/970) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.126 (Fri Oct 14 2022)

#### 🐛 Bug Fix

- changing logs error to info [#968](https://github.com/Subscribie/subscribie/pull/968) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.125 (Thu Oct 13 2022)

#### 🐛 Bug Fix

- Fix #966 changing logs from error to info [#967](https://github.com/Subscribie/subscribie/pull/967) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.124 (Thu Oct 13 2022)

#### ⚠️ Pushed to `master`

- reduce default currency error to info subscribie/utils.py ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.123 (Thu Oct 13 2022)

#### 🐛 Bug Fix

- Fix #964 Add SUPPORTED_CURRENCIES to .envsubst.template [#965](https://github.com/Subscribie/subscribie/pull/965) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.122 (Thu Oct 13 2022)

#### 🐛 Bug Fix

- #962 debug logging showIntervalAmount [#963](https://github.com/Subscribie/subscribie/pull/963) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #962 debug getIntervalAmount [#963](https://github.com/Subscribie/subscribie/pull/963) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #962 get_geo_country_code log country_code [#963](https://github.com/Subscribie/subscribie/pull/963) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip fix #962 log get_geo_currency_code currency_code [#963](https://github.com/Subscribie/subscribie/pull/963) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.121 (Thu Oct 13 2022)

#### 🐛 Bug Fix

- 482 As a shop owner I can sell in USD currency [#757](https://github.com/Subscribie/subscribie/pull/757) ([@joeltejeda](https://github.com/joeltejeda) [@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.120 (Wed Oct 12 2022)

#### 🐛 Bug Fix

- #960 remove undeeded -i tests/delete_stripe_accounts_bulk.py leftover from debugging [#961](https://github.com/Subscribie/subscribie/pull/961) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #960 add heading link to bulk delete stripe accounts [#961](https://github.com/Subscribie/subscribie/pull/961) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #960 tests/delete_stripe_accounts_bulk.py & document [#961](https://github.com/Subscribie/subscribie/pull/961) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.119 (Wed Oct 12 2022)

#### 🐛 Bug Fix

- Fix #958 removing unneeded stripe onboarding steps [#959](https://github.com/Subscribie/subscribie/pull/959) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.118 (Tue Oct 11 2022)

#### 🐛 Bug Fix

- Fix #956 rearreging black inside pr-demo-deploy github action [#957](https://github.com/Subscribie/subscribie/pull/957) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.117 (Sun Oct 09 2022)

#### 🐛 Bug Fix

- Fix #954 log error if module subscribie imports fail [#955](https://github.com/Subscribie/subscribie/pull/955) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.116 (Sun Oct 09 2022)

#### 🐛 Bug Fix

- #951 bring migrations up to black format [#953](https://github.com/Subscribie/subscribie/pull/953) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.115 (Sat Oct 08 2022)

#### 🐛 Bug Fix

- #951 added psf/black@stable action step [#952](https://github.com/Subscribie/subscribie/pull/952) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.114 (Sat Oct 08 2022)

#### ⚠️ Pushed to `master`

- wip #951 black format missed out forms/models.py ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.113 (Sat Oct 08 2022)

#### 🐛 Bug Fix

- Fix #949 f strings on module import logging [#950](https://github.com/Subscribie/subscribie/pull/950) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### 🔩 Dependency Updates

- Bump jpeg-js and @playwright/test [#948](https://github.com/Subscribie/subscribie/pull/948) ([@dependabot[bot]](https://github.com/dependabot[bot]))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@dependabot[bot]](https://github.com/dependabot[bot])

---

# v0.1.112 (Wed Sep 28 2022)

#### 🐛 Bug Fix

- #944 type hint admin id int [#945](https://github.com/Subscribie/subscribie/pull/945) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #994 deleting admin account by id [#945](https://github.com/Subscribie/subscribie/pull/945) ([@joeltejeda](https://github.com/joeltejeda))
- Fix #994 superadmin account cant be deleted [#945](https://github.com/Subscribie/subscribie/pull/945) ([@joeltejeda](https://github.com/joeltejeda))
- #944 put "Delete Shop Admin" button below "Add Shop Admin" [#945](https://github.com/Subscribie/subscribie/pull/945) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #944 rename "Delete an Admin Account" -> "Delete Shop Admin" [#945](https://github.com/Subscribie/subscribie/pull/945) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #944 delete admin account feature [#945](https://github.com/Subscribie/subscribie/pull/945) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.111 (Mon Sep 12 2022)

#### 🐛 Bug Fix

- renaming to have parity with stripe docs [#943](https://github.com/Subscribie/subscribie/pull/943) ([@joeltejeda](https://github.com/joeltejeda))
- adding default value to column stripe_active [#943](https://github.com/Subscribie/subscribie/pull/943) ([@joeltejeda](https://github.com/joeltejeda))
- #942 refactoring [#943](https://github.com/Subscribie/subscribie/pull/943) ([@joeltejeda](https://github.com/joeltejeda))
- #942 updating route to check if stripe is linked [#943](https://github.com/Subscribie/subscribie/pull/943) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.110 (Mon Sep 12 2022)

#### 🐛 Bug Fix

- updating stripe onboarding [#940](https://github.com/Subscribie/subscribie/pull/940) ([@joeltejeda](https://github.com/joeltejeda))
- adding free plan test [#940](https://github.com/Subscribie/subscribie/pull/940) ([@joeltejeda](https://github.com/joeltejeda))
- #939 added Plan.is_free() utility method [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #939 update choose.html to show "Free" when plan is free [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #939 add free plan to seed.sql so `flask initdb` inserts test free plan [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #939 remove database.session.commit() not needed because db commits are handled atomically within the execution of create_subscription and no surounding db changes [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #939 no need to pass subscribie_checkout_session_id, stripe_subscription_id, or stripe_external_id because the default is none (see def create_subscription) [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #939 dont assume chosen_option_ids exists, not all plans have options (KeyError: chosen_option_ids) [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #939 use Plan.requirements to check if is a free plan [#940](https://github.com/Subscribie/subscribie/pull/940) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding free plan creation without stripe connect [#940](https://github.com/Subscribie/subscribie/pull/940) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.109 (Mon Aug 22 2022)

#### 🐛 Bug Fix

- ref #937 bring back usage of IMAP_SEARCH_UNSEEN so is configurable [#938](https://github.com/Subscribie/subscribie/pull/938) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- fix #937 update env playwright test example [#938](https://github.com/Subscribie/subscribie/pull/938) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.108 (Fri Aug 19 2022)

#### 🐛 Bug Fix

- Added Features Link to footer [#933](https://github.com/Subscribie/subscribie/pull/933) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.107 (Fri Aug 19 2022)

#### 🐛 Bug Fix

- fixing database session was never closed [#919](https://github.com/Subscribie/subscribie/pull/919) ([@joeltejeda](https://github.com/joeltejeda))
- refactoring [#919](https://github.com/Subscribie/subscribie/pull/919) ([@joeltejeda](https://github.com/joeltejeda))
- #918 check if stripe event webhook livemode is equal to database stripe_livemode [#919](https://github.com/Subscribie/subscribie/pull/919) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.106 (Mon Aug 15 2022)

#### ⚠️ Pushed to `master`

- #932 remive honeycomb ([@chrisjsimpson](https://github.com/chrisjsimpson))
- fix #934 wip remove undeeded settings ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.105 (Tue Aug 09 2022)

#### 🐛 Bug Fix

- udpate stripe onboarding 3 [#929](https://github.com/Subscribie/subscribie/pull/929) ([@joeltejeda](https://github.com/joeltejeda))
- deleting connect account id if stripe was not connected succesfully [#929](https://github.com/Subscribie/subscribie/pull/929) ([@joeltejeda](https://github.com/joeltejeda))
- updating stripe onboarding2 [#929](https://github.com/Subscribie/subscribie/pull/929) ([@joeltejeda](https://github.com/joeltejeda))
- update stripe onboarding [#929](https://github.com/Subscribie/subscribie/pull/929) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.104 (Tue Aug 09 2022)

#### 🐛 Bug Fix

- Fix #930 show url to plan in api get plan output [#931](https://github.com/Subscribie/subscribie/pull/931) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.103 (Mon Aug 08 2022)

#### 🐛 Bug Fix

- #927 re-order and re-word footer links [#928](https://github.com/Subscribie/subscribie/pull/928) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Updating Landing Page Links with Relevant Keywords [#928](https://github.com/Subscribie/subscribie/pull/928) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- fixed landing page link [#928](https://github.com/Subscribie/subscribie/pull/928) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- Spelling Correction to site footer (Landing Pages) [#928](https://github.com/Subscribie/subscribie/pull/928) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))
- adding footer header and fixing missed end of div [#928](https://github.com/Subscribie/subscribie/pull/928) ([@joeltejeda](https://github.com/joeltejeda))
- Add Landing Page [#928](https://github.com/Subscribie/subscribie/pull/928) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 3

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@jimmyedagawa78](https://github.com/jimmyedagawa78)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.102 (Fri Jul 29 2022)

:tada: This release contains work from a new contributor! :tada:

Thank you, null[@jimmyedagawa78](https://github.com/jimmyedagawa78), for all your work!

#### 🐛 Bug Fix

- update choose.html [#926](https://github.com/Subscribie/subscribie/pull/926) ([@jimmyedagawa78](https://github.com/jimmyedagawa78))

#### Authors: 1

- [@jimmyedagawa78](https://github.com/jimmyedagawa78)

---

# v0.1.101 (Mon Jul 04 2022)

#### 🐛 Bug Fix

- Fix #921 move "More Details" plan description to below selling points of plan [#922](https://github.com/Subscribie/subscribie/pull/922) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #921 adding description template to plans [#922](https://github.com/Subscribie/subscribie/pull/922) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.100 (Tue Jun 21 2022)

#### 🐛 Bug Fix

- #915 github.head_ref -> env.SUBDOMAIN [#917](https://github.com/Subscribie/subscribie/pull/917) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.99 (Mon Jun 20 2022)

#### 🐛 Bug Fix

- Fix #915 demo-videos syntax [#916](https://github.com/Subscribie/subscribie/pull/916) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.98 (Mon Jun 20 2022)

#### ⚠️ Pushed to `master`

- Update demo-videos.yml ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.97 (Mon Jun 20 2022)

#### 🐛 Bug Fix

- updating onboarding stripe 2 [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- updating stripe onboarding steps [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- missing one character for the or statement [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- only restarting dokku container if mounting the email-queue folder for the first time [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- true if already exist [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- fixing misspelling [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- mounting email queue folder [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- adding back the http to development [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- #913 adding queue email folder [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- refactoring email sending to magic login and reset password [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- removing http on development environment [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))
- #913 changing test subscriber user with a new valid test mail [#914](https://github.com/Subscribie/subscribie/pull/914) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.96 (Mon Jun 13 2022)

#### 🐛 Bug Fix

- #910 center get started and demo shop button [#912](https://github.com/Subscribie/subscribie/pull/912) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.95 (Mon Jun 13 2022)

#### 🐛 Bug Fix

- ordering upfront plan with test user [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- removing special characters [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- debug 3 [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- removing debug 2 [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- removing debug [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- removing password url from logs [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- removing password reset url https when running in development mode [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))
- updating subscriber magic login test [#729](https://github.com/Subscribie/subscribie/pull/729) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.94 (Sat Jun 11 2022)

#### ⚠️ Pushed to `master`

- Update README.md ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.93 (Wed Jun 08 2022)

#### 🐛 Bug Fix

- Fix #908 show link to live demo try [#909](https://github.com/Subscribie/subscribie/pull/909) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.92 (Tue May 31 2022)

#### 🐛 Bug Fix

- updating stripe onboarding steps [#906](https://github.com/Subscribie/subscribie/pull/906) ([@joeltejeda](https://github.com/joeltejeda))
- #905 testing filtering by subscriber name and email [#906](https://github.com/Subscribie/subscribie/pull/906) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.91 (Tue May 31 2022)

#### 🐛 Bug Fix

- #886 Shop owner can search by name & email at the same time (inclusive search) [#895](https://github.com/Subscribie/subscribie/pull/895) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- close #885 warn shop owner when search filter is applied to subscribers [#895](https://github.com/Subscribie/subscribie/pull/895) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #885 keep searched subscriber name/email between searches so shop owner does not need to re-type [#895](https://github.com/Subscribie/subscribie/pull/895) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #885 filtering subscribers by name and email [#895](https://github.com/Subscribie/subscribie/pull/895) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.90 (Tue May 31 2022)

#### 🐛 Bug Fix

- adding workflow badges to the the readme [#904](https://github.com/Subscribie/subscribie/pull/904) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.89 (Mon May 30 2022)

#### 🐛 Bug Fix

- #900 restore collect-membership-fees.html [#901](https://github.com/Subscribie/subscribie/pull/901) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #900 myFunction -> toggleDropdown [#901](https://github.com/Subscribie/subscribie/pull/901) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #900 "Register -> Start now" [#901](https://github.com/Subscribie/subscribie/pull/901) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #900 restore "Why Subsctibie" to footer [#901](https://github.com/Subscribie/subscribie/pull/901) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #900 restore subscriptionbilling.html [#901](https://github.com/Subscribie/subscribie/pull/901) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #900 restore subscriptionsoftware.html [#901](https://github.com/Subscribie/subscribie/pull/901) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #900 restructure builder theme [#901](https://github.com/Subscribie/subscribie/pull/901) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.88 (Mon May 16 2022)

#### 🐛 Bug Fix

- filtering subscription for trialing and active [#897](https://github.com/Subscribie/subscribie/pull/897) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.87 (Mon May 16 2022)

#### 🐛 Bug Fix

- removing official name attribute [#894](https://github.com/Subscribie/subscribie/pull/894) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.86 (Sun May 15 2022)

#### 🐛 Bug Fix

- #886 default countryObj to None [#892](https://github.com/Subscribie/subscribie/pull/892) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #886 dynamic country detection [#892](https://github.com/Subscribie/subscribie/pull/892) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.85 (Sat May 14 2022)

#### 🐛 Bug Fix

- Merge branch '886-store-client-request-country-in-request-header' of github.com:Subscribie/subscribie into 886-store-client-request-country-in-request-header [#887](https://github.com/Subscribie/subscribie/pull/887) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### 🔩 Dependency Updates

- Fix #888 upgrade to python 3.10 [#889](https://github.com/Subscribie/subscribie/pull/889) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.84 (Sat May 07 2022)

#### 🐛 Bug Fix

- adding back the 3 workers at a time [#883](https://github.com/Subscribie/subscribie/pull/883) ([@joeltejeda](https://github.com/joeltejeda))
- #881 using globalteardown as an env variable to enable and disable it [#883](https://github.com/Subscribie/subscribie/pull/883) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.83 (Fri May 06 2022)

#### 🐛 Bug Fix

- #878 adding github action to remove pr preview after merge [#880](https://github.com/Subscribie/subscribie/pull/880) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.82 (Thu May 05 2022)

#### ⚠️ Pushed to `master`

- Update README.md ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.81 (Sat Apr 30 2022)

#### 🐛 Bug Fix

- wip #866 added Shop schema (pydantic) [#867](https://github.com/Subscribie/subscribie/pull/867) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.80 (Fri Apr 29 2022)

#### 🐛 Bug Fix

- #209 changing connect to stripe wording [#876](https://github.com/Subscribie/subscribie/pull/876) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.79 (Fri Apr 29 2022)

#### 🐛 Bug Fix

- adding edit plan suppoed image text [#877](https://github.com/Subscribie/subscribie/pull/877) ([@joeltejeda](https://github.com/joeltejeda))
- #227 adding upload supported list and adding webp image extension [#877](https://github.com/Subscribie/subscribie/pull/877) ([@joeltejeda](https://github.com/joeltejeda))
- adding uploads to the filter path [#877](https://github.com/Subscribie/subscribie/pull/877) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.78 (Fri Apr 29 2022)

#### 🐛 Bug Fix

- adding delete connect account id test after all tests [#875](https://github.com/Subscribie/subscribie/pull/875) ([@joeltejeda](https://github.com/joeltejeda))
- renaming delete connect account id [#875](https://github.com/Subscribie/subscribie/pull/875) ([@joeltejeda](https://github.com/joeltejeda))
- re-adding delete connect accound id test [#875](https://github.com/Subscribie/subscribie/pull/875) ([@joeltejeda](https://github.com/joeltejeda))
- deleting connect account id after all workers [#875](https://github.com/Subscribie/subscribie/pull/875) ([@joeltejeda](https://github.com/joeltejeda))
- #600 replacing paytoday with upfrontcost, adding the total and removing duplicated html theme [#875](https://github.com/Subscribie/subscribie/pull/875) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.77 (Thu Apr 28 2022)

#### 🐛 Bug Fix

- allowing custom pages to have numbers and letters [#874](https://github.com/Subscribie/subscribie/pull/874) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.76 (Thu Apr 28 2022)

#### 🐛 Bug Fix

- testing logo upload [#873](https://github.com/Subscribie/subscribie/pull/873) ([@joeltejeda](https://github.com/joeltejeda))
- adding subscribie logo [#873](https://github.com/Subscribie/subscribie/pull/873) ([@joeltejeda](https://github.com/joeltejeda))
- #872 uploading subscribie logo into hair gel plan [#873](https://github.com/Subscribie/subscribie/pull/873) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.75 (Wed Apr 27 2022)

#### 🐛 Bug Fix

- adding custom bootstrap css navbar [#871](https://github.com/Subscribie/subscribie/pull/871) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.74 (Wed Apr 27 2022)

#### 🐛 Bug Fix

- reverting [#870](https://github.com/Subscribie/subscribie/pull/870) ([@joeltejeda](https://github.com/joeltejeda))
- Revert "#620 adding question about card expiration" [#870](https://github.com/Subscribie/subscribie/pull/870) ([@joeltejeda](https://github.com/joeltejeda))
- making the test slower [#870](https://github.com/Subscribie/subscribie/pull/870) ([@joeltejeda](https://github.com/joeltejeda))
- #620 adding question about card expiration [#870](https://github.com/Subscribie/subscribie/pull/870) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.73 (Mon Apr 25 2022)

#### 🐛 Bug Fix

- changing colour contrast for Order Summary [#869](https://github.com/Subscribie/subscribie/pull/869) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.72 (Mon Apr 25 2022)

#### 🐛 Bug Fix

- housekeeping3.1 [#868](https://github.com/Subscribie/subscribie/pull/868) ([@joeltejeda](https://github.com/joeltejeda))
- housekeeping3 [#868](https://github.com/Subscribie/subscribie/pull/868) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.71 (Mon Apr 25 2022)

#### 🐛 Bug Fix

- adding variable name [#863](https://github.com/Subscribie/subscribie/pull/863) ([@joeltejeda](https://github.com/joeltejeda))
- housekeeping [#863](https://github.com/Subscribie/subscribie/pull/863) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.70 (Mon Apr 25 2022)

#### 🐛 Bug Fix

- Update pr-demo-deploy.yml [#862](https://github.com/Subscribie/subscribie/pull/862) ([@joeltejeda](https://github.com/joeltejeda))
- deleting taxrate table and deleting connect account id [#862](https://github.com/Subscribie/subscribie/pull/862) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.69 (Fri Apr 22 2022)

#### 🐛 Bug Fix

- Fix #864 added missing subscriber-payment-failed-notification email template [#865](https://github.com/Subscribie/subscribie/pull/865) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.68 (Fri Apr 08 2022)

#### 🐛 Bug Fix

- #857 adding charge date to shop owner failed and failing invoices [#858](https://github.com/Subscribie/subscribie/pull/858) ([@joeltejeda](https://github.com/joeltejeda))
- adding subscriber Charge date using database column created [#858](https://github.com/Subscribie/subscribie/pull/858) ([@joeltejeda](https://github.com/joeltejeda))
- fetching stripe invoice created date [#858](https://github.com/Subscribie/subscribie/pull/858) ([@joeltejeda](https://github.com/joeltejeda))
- #857 adding created at and created columns inside stripe_invoices [#858](https://github.com/Subscribie/subscribie/pull/858) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.67 (Wed Apr 06 2022)

#### ⚠️ Pushed to `master`

- add first video demo to readme ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.66 (Wed Apr 06 2022)

#### ⚠️ Pushed to `master`

- Update README.md ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.65 (Wed Apr 06 2022)

#### 🐛 Bug Fix

- Merge branch '783-as-subscriber-notification-when-payment-fails' [#848](https://github.com/Subscribie/subscribie/pull/848) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.64 (Wed Apr 06 2022)

#### ⚠️ Pushed to `master`

- Make demo shop picture link clickable ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.63 (Sun Apr 03 2022)

#### 🐛 Bug Fix

- ref #852 new_domain escape [#856](https://github.com/Subscribie/subscribie/pull/856) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.62 (Sun Apr 03 2022)

#### 🐛 Bug Fix

- Fix #853 Fix test announcer action [#854](https://github.com/Subscribie/subscribie/pull/854) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.61 (Sun Apr 03 2022)

#### 🐛 Bug Fix

- maintainability housekeeping [#852](https://github.com/Subscribie/subscribie/pull/852) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.60 (Sat Apr 02 2022)

#### 🐛 Bug Fix

- Fix #214 Shop owner can "View my shop" from dashboard" [#850](https://github.com/Subscribie/subscribie/pull/850) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.59 (Sat Apr 02 2022)

#### 🐛 Bug Fix

- Fix #201 faq page typos [#847](https://github.com/Subscribie/subscribie/pull/847) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.58 (Sat Apr 02 2022)

#### 🐛 Bug Fix

- #845 dont redirect using request.referrer, send to well known path admin.subscribers [#846](https://github.com/Subscribie/subscribie/pull/846) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #845 introduce background_task decorator & make update_stripe_subscription_statuses non blocking [#846](https://github.com/Subscribie/subscribie/pull/846) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.57 (Fri Apr 01 2022)

#### 🐛 Bug Fix

- removing shopowner login when they already are in [#840](https://github.com/Subscribie/subscribie/pull/840) ([@joeltejeda](https://github.com/joeltejeda))
- deleting unnecesary <p> tags [#840](https://github.com/Subscribie/subscribie/pull/840) ([@joeltejeda](https://github.com/joeltejeda))
- #836 adding account and logout buttons for subscribers template [#840](https://github.com/Subscribie/subscribie/pull/840) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.56 (Fri Apr 01 2022)

#### 🐛 Bug Fix

- #841 add logging to get_stripe_invoices [#842](https://github.com/Subscribie/subscribie/pull/842) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #841 pass current_app to get_stripe_invoices [#842](https://github.com/Subscribie/subscribie/pull/842) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- remove duplication in get_stripe_invoices by making app context required #841 [#842](https://github.com/Subscribie/subscribie/pull/842) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Set http response code to 202 for /admin/refresh-invoices #841 [#842](https://github.com/Subscribie/subscribie/pull/842) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #841 remove debug statement [#842](https://github.com/Subscribie/subscribie/pull/842) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #841 putting refresh-invoices path to use threads [#842](https://github.com/Subscribie/subscribie/pull/842) ([@joeltejeda](https://github.com/joeltejeda))
- #837 keep fix for when logged in subscriber subscribes to new plan- but remove additional email "newplan.jinja2.html" as not needed [#843](https://github.com/Subscribie/subscribie/pull/843) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #837 spelling + wording newplan.jinja2.html [#843](https://github.com/Subscribie/subscribie/pull/843) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- filtering paths to let subscribers buy plans while logged in [#843](https://github.com/Subscribie/subscribie/pull/843) ([@joeltejeda](https://github.com/joeltejeda))
- creating a new email template for logged subscribers [#843](https://github.com/Subscribie/subscribie/pull/843) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.55 (Tue Mar 29 2022)

#### 🐛 Bug Fix

- Merge branch 'master' of github.com:Subscribie/subscribie [#811](https://github.com/Subscribie/subscribie/pull/811) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### 🔩 Dependency Updates

- Bump minimist from 1.2.5 to 1.2.6 [#833](https://github.com/Subscribie/subscribie/pull/833) ([@dependabot[bot]](https://github.com/dependabot[bot]))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@dependabot[bot]](https://github.com/dependabot[bot])

---

# v0.1.54 (Fri Mar 25 2022)

#### ⚠️ Pushed to `master`

- updating update-onboarding-sites ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.53 (Fri Mar 25 2022)

#### 🐛 Bug Fix

- #831 reducing naming ambiguity [#832](https://github.com/Subscribie/subscribie/pull/832) ([@joeltejeda](https://github.com/joeltejeda))
- adding connect-account-id deletion after the test ends [#832](https://github.com/Subscribie/subscribie/pull/832) ([@joeltejeda](https://github.com/joeltejeda))
- adding delete-connect-account url [#832](https://github.com/Subscribie/subscribie/pull/832) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.52 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation update-onboarding-site ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.51 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation update-all-sites ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.50 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation python-package ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.49 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation demo-videos ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.48 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation container-publish ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.47 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation codeql-analysis ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.46 (Sat Mar 12 2022)

#### ⚠️ Pushed to `master`

- #829 correct paths-ignore indentation ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.45 (Sat Mar 12 2022)

#### 🐛 Bug Fix

- Fix #829 Dont rebuild on readme changes [#830](https://github.com/Subscribie/subscribie/pull/830) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### ⚠️ Pushed to `master`

- Ref #829 to tag a new release when the readme changes ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.44 (Sat Mar 12 2022)

#### 🐛 Bug Fix

- #826 Bump playwright to ^1.19.2 [#827](https://github.com/Subscribie/subscribie/pull/827) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- lint F841 [#827](https://github.com/Subscribie/subscribie/pull/827) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #826 include cancelled Stripe subscriptions in update_stripe_subscription_statuses [#827](https://github.com/Subscribie/subscribie/pull/827) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.43 (Tue Mar 08 2022)

#### 🐛 Bug Fix

- fixing font color headers [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))
- adding test font color [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))
- adding css font colors from homepage [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))
- changing colors and background [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))
- wip changing background and color [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))
- wip changing font colors [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))
- adding font colours [#812](https://github.com/Subscribie/subscribie/pull/812) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.42 (Tue Mar 08 2022)

#### ⚠️ Pushed to `master`

- Update README.md ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.41 (Tue Mar 08 2022)

#### ⚠️ Pushed to `master`

- Merge branch 'master' of github.com:Subscribie/subscribie ([@chrisjsimpson](https://github.com/chrisjsimpson))
- default api keys to none in template #820 ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.40 (Tue Mar 08 2022)

#### ⚠️ Pushed to `master`

- #820 handle case where api token not yet set ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.39 (Tue Mar 08 2022)

#### 🐛 Bug Fix

- #820 remove unused var [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #820 #820 allow api token authentication [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #820 as shop owner/developer I can see the shop api keys and re-generate them #821 [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- ref #820 return fetch-live-api-key/fetch-test-api-key after generation [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #820 encrypt api key storage at rest [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #820 store api keys in Settings [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #820 generate test/live api key [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #820 add api_key_secret_live & api_key_secret_test to Setting model [#822](https://github.com/Subscribie/subscribie/pull/822) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.38 (Sat Mar 05 2022)

#### 🐛 Bug Fix

- Fix #818 remove old kubernetes manifests [#819](https://github.com/Subscribie/subscribie/pull/819) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #818 remove jenkinsx [#819](https://github.com/Subscribie/subscribie/pull/819) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.37 (Fri Mar 04 2022)

#### ⚠️ Pushed to `master`

- document stripe-connect-account-announcer and stripe-connect-account-announcer ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.36 (Tue Mar 01 2022)

#### 🐛 Bug Fix

- Fix #815 email notify shop owner when a subscription payment collection fails [#817](https://github.com/Subscribie/subscribie/pull/817) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #815 log payment_intent.payment_failed events [#817](https://github.com/Subscribie/subscribie/pull/817) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.35 (Sun Feb 27 2022)

#### ⚠️ Pushed to `master`

- Update README stripe cli include payment_intent.payment_failed ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.34 (Sun Feb 27 2022)

#### 🐛 Bug Fix

- Fix #815 email notify shop owner when a subscription payment collection fails [#816](https://github.com/Subscribie/subscribie/pull/816) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- wip #815 log payment_intent.payment_failed events [#816](https://github.com/Subscribie/subscribie/pull/816) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.33 (Sun Feb 27 2022)

#### ⚠️ Pushed to `master`

- Hotfix - don't attempt to get Stripe Subscription if subscription.stripe_subscription_id is None ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.32 (Sun Feb 27 2022)

#### 🐛 Bug Fix

- Fix #813 show subscriber mobile friendly [#814](https://github.com/Subscribie/subscribie/pull/814) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.31 (Tue Feb 22 2022)

#### ⚠️ Pushed to `master`

- Update README.md ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.30 (Tue Feb 22 2022)

#### ⚠️ Pushed to `master`

- Add developer container quickstart example ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.29 (Tue Feb 22 2022)

#### 🐛 Bug Fix

- modifying feature playwright test [#810](https://github.com/Subscribie/subscribie/pull/810) ([@joeltejeda](https://github.com/joeltejeda))
- fix #803 adding pause and resume confirmation [#810](https://github.com/Subscribie/subscribie/pull/810) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.28 (Tue Feb 22 2022)

#### 🐛 Bug Fix

- removing logging in because test is already logged in [#807](https://github.com/Subscribie/subscribie/pull/807) ([@joeltejeda](https://github.com/joeltejeda))
- removing debugging code [#807](https://github.com/Subscribie/subscribie/pull/807) ([@joeltejeda](https://github.com/joeltejeda))
- fix #806 upgrading refresh subscriptions feature [#807](https://github.com/Subscribie/subscribie/pull/807) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.27 (Tue Feb 22 2022)

#### 🐛 Bug Fix

- Fix #808 bump flask to version 2 [#809](https://github.com/Subscribie/subscribie/pull/809) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.26 (Sun Feb 20 2022)

#### 🐛 Bug Fix

- #801 enable ondemand and socket activation uwsgi [#802](https://github.com/Subscribie/subscribie/pull/802) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #801 document socket activation and onDemandVassals [#802](https://github.com/Subscribie/subscribie/pull/802) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #801 document systemd and uwsgi emperor usage [#802](https://github.com/Subscribie/subscribie/pull/802) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #801 set subscribie systemd emperor config to emperor.ini [#802](https://github.com/Subscribie/subscribie/pull/802) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #801 add common vassal config to vassals-inject-config.ini [#802](https://github.com/Subscribie/subscribie/pull/802) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #801 wip document socket activation [#802](https://github.com/Subscribie/subscribie/pull/802) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.25 (Sat Feb 19 2022)

#### 🐛 Bug Fix

- Ref #796 systemd journalctl logging subscribie [#800](https://github.com/Subscribie/subscribie/pull/800) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.24 (Fri Feb 18 2022)

#### 🐛 Bug Fix

- #798 fixing stripe test mode to skip subscribing to a plan [#799](https://github.com/Subscribie/subscribie/pull/799) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.23 (Fri Feb 18 2022)

#### 🐛 Bug Fix

- typo #796 [#797](https://github.com/Subscribie/subscribie/pull/797) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- adding systemctl file config [#797](https://github.com/Subscribie/subscribie/pull/797) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 2

- [@chrisjsimpson](https://github.com/chrisjsimpson)
- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.22 (Thu Feb 17 2022)

#### 🐛 Bug Fix

- adding rename script into deploy template [#795](https://github.com/Subscribie/subscribie/pull/795) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.21 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- changing variable naame to new_name [#792](https://github.com/Subscribie/subscribie/pull/792) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.20 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- Fix #789 add plan validation duplicate use of id [#790](https://github.com/Subscribie/subscribie/pull/790) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.19 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- Fix #787 return 200 after refreshing subscriptions [#788](https://github.com/Subscribie/subscribie/pull/788) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.18 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- 778 add navbar register button [#782](https://github.com/Subscribie/subscribie/pull/782) ([@elliottmotson](https://github.com/elliottmotson))

#### Authors: 1

- Elliott Sabin-Motson ([@elliottmotson](https://github.com/elliottmotson))

---

# v0.1.17 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- 778 add navbar register button [#781](https://github.com/Subscribie/subscribie/pull/781) ([@elliottmotson](https://github.com/elliottmotson))

#### Authors: 1

- Elliott Sabin-Motson ([@elliottmotson](https://github.com/elliottmotson))

---

# v0.1.16 (Wed Feb 16 2022)

:tada: This release contains work from a new contributor! :tada:

Thank you, Elliott Sabin-Motson ([@elliottmotson](https://github.com/elliottmotson)), for all your work!

#### 🐛 Bug Fix

- Edited navbar element to include "/" char divider [#780](https://github.com/Subscribie/subscribie/pull/780) ([@elliottmotson](https://github.com/elliottmotson))
- Added navbar element "Register" with hardcoded subscribie.co.uk link [#780](https://github.com/Subscribie/subscribie/pull/780) ([@elliottmotson](https://github.com/elliottmotson))

#### Authors: 1

- Elliott Sabin-Motson ([@elliottmotson](https://github.com/elliottmotson))

---

# v0.1.15 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- 680 instant onboarding [#777](https://github.com/Subscribie/subscribie/pull/777) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.14 (Wed Feb 16 2022)

#### 🐛 Bug Fix

- 680 instant onboarding [#774](https://github.com/Subscribie/subscribie/pull/774) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.13 (Mon Feb 14 2022)

#### ⚠️ Pushed to `master`

- Revert "adding jinjax reverse (#776)" ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.12 (Mon Feb 14 2022)

#### 🐛 Bug Fix

- adding jinjax reverse [#776](https://github.com/Subscribie/subscribie/pull/776) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.11 (Wed Jan 26 2022)

#### 🐛 Bug Fix

- 769 shop owner can activate their own shop [#770](https://github.com/Subscribie/subscribie/pull/770) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.10 (Tue Jan 25 2022)

#### 🐛 Bug Fix

- Fix #771 auto redirect to shop owner dashboard from login page if already logged in [#772](https://github.com/Subscribie/subscribie/pull/772) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.9 (Tue Jan 18 2022)

#### 🐛 Bug Fix

- Fix #766 show shops list [#767](https://github.com/Subscribie/subscribie/pull/767) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.8 (Thu Jan 13 2022)

#### 🐛 Bug Fix

- Fix #763 update requirements from requirements.txt during update all sites [#764](https://github.com/Subscribie/subscribie/pull/764) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.7 (Thu Jan 13 2022)

#### 🐛 Bug Fix

- Merge branch '752-update-wtf-forms' [#753](https://github.com/Subscribie/subscribie/pull/753) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.6 (Tue Jan 11 2022)

#### 🐛 Bug Fix

- removing dokku apps every merge [#761](https://github.com/Subscribie/subscribie/pull/761) ([@joeltejeda](https://github.com/joeltejeda))
- adding concurrency github group [#761](https://github.com/Subscribie/subscribie/pull/761) ([@joeltejeda](https://github.com/joeltejeda))
- #748 stopping any workflow running and deleting dokku app [#761](https://github.com/Subscribie/subscribie/pull/761) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.5 (Tue Jan 11 2022)

#### 🐛 Bug Fix

- adding timeout to stripe announcer [#760](https://github.com/Subscribie/subscribie/pull/760) ([@joeltejeda](https://github.com/joeltejeda))

#### Authors: 1

- [@joeltejeda](https://github.com/joeltejeda)

---

# v0.1.4 (Sun Jan 09 2022)

#### 🐛 Bug Fix

- ref #746 display ad-hoc charges on transactions dashboard & transactions export [#747](https://github.com/Subscribie/subscribie/pull/747) ([@chrisjsimpson](https://github.com/chrisjsimpson))
- Fix #746 stripe webhook when ad-hoc charge is made, dont try and retrieve invice from stripe because there is none [#747](https://github.com/Subscribie/subscribie/pull/747) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.3 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- Merge branch 'master' of github.com:Subscribie/subscribie ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #754 set auto release user to subscribie-bot ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.2 (Sun Jan 09 2022)

#### 🐛 Bug Fix

- 754 automatically tag releases [#756](https://github.com/Subscribie/subscribie/pull/756) ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.1 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- #754 remove plugin all-contributors to remove node dep ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #754 update auto ship plugins ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.1 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- #754 remove plugin all-contributors to remove node dep ([@chrisjsimpson](https://github.com/chrisjsimpson))
- #754 update auto ship plugins ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.1 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- #754 update auto ship plugins ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.1 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- #754 update auto ship plugins ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.1 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- #754 update auto ship plugins ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)

---

# v0.1.1 (Sun Jan 09 2022)

#### ⚠️ Pushed to `master`

- #754 update auto ship plugins ([@chrisjsimpson](https://github.com/chrisjsimpson))

#### Authors: 1

- [@chrisjsimpson](https://github.com/chrisjsimpson)
