const { test, expect } = require('@playwright/test');
const TEST = process.env.TEST;
test.describe("Github actions test:", () => {
const magic_login_receives_email = require(`./tests/${TEST}/704_shop_owner_magic_login_receives_email`);

});
