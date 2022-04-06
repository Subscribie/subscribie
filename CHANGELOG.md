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
