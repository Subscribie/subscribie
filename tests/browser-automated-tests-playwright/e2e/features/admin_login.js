var admin_login = async function (page) {
    await page.goto(process.env['PLAYWRIGHT_HOST'] + '/auth/login');
    await page.fill('#email', 'admin@example.com');
    await page.fill('#password', 'password');
    await page.click('#login');
    await page.goto(process.env['PLAYWRIGHT_HOST'] + '/admin/dashboard');
}


module.exports.admin_login = admin_login