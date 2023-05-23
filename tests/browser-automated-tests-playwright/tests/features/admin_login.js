
async function admin_login(page) {

  await page.goto('/auth/login');
  await page.fill('#email', 'admin@example.com');
  await page.fill('#password', 'password');
  await page.click('#login');
}     

module.exports = admin_login;