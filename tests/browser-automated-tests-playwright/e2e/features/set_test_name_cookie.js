var set_test_name_cookie = async function (page, testName) {
    /* Drop a cookie to cause Subscribie to display a visual
    feedback overlay showing the test name/number running at the time.
    */
    await page.goto(`/admin/set-test-name/${testName}`);

    //await new Promise(x => setTimeout(x, 19000));
}

module.exports.set_test_name_cookie = set_test_name_cookie;