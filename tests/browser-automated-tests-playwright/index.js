require('dotenv').config()

test_order_plan_with_subscription_and_upfront_charge = require('./tests/test_order_plan_with_subscription_and_upfront_charge');
test_order_plan_with_only_upfront_charge = require('./tests/test_order_plan_with_only_upfront_charge');
test_order_plan_with_only_recurring_charge = require('./tests/test_order_plan_with_only_recurring_charge');

const playwright = require('playwright');
const devices = playwright.devices;
const assert = require('assert');
const DEFAULT_TIMEOUT = 10000

//const browsers = ['chromium', 'webkit'];
const browsers = ['chromium'];

const iPhone = devices['iPhone 6'];

// Delete any existing persons & subscriptions from the database
async function clearDB() {
  const sqlite3 = require('sqlite3').verbose();
  const db = new sqlite3.Database(process.env.DB_FULL_PATH);

  db.serialize(function() {

    console.log("Deleting subscriptions");
    db.run("DELETE from subscription");

    console.log("Deleting persons");
    db.run("DELETE from person");

    console.log("Deleting transactions");
    db.run("DELETE from transactions");
   
  });
   
  db.close();
}


(async() => {
  clearDB();
  await test_order_plan_with_subscription_and_upfront_charge(browsers);
  clearDB();
  await test_order_plan_with_only_upfront_charge(browsers);
  clearDB();
  await test_order_plan_with_only_recurring_charge(browsers);
  clearDB();
  await test_order_plan_with_only_recurring_charge(browsers);

  clearDB();
})();
