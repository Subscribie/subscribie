const https = require('https')

function checkShopOwnerLogin() {
  const SHOP_OWNER_EMAIL_HOST = process.env.SHOP_OWNER_EMAIL_HOST
  const SHOP_OWNER_EMAIL_USER = process.env.SHOP_OWNER_EMAIL_USER
  const SHOP_OWNER_EMAIL_PASSWORD = process.env.SHOP_OWNER_EMAIL_PASSWORD
  const IMAP_SEARCH_UNSEEN = parseInt(process.env.IMAP_SEARCH_UNSEEN)
  const MAGIC_LOGIN_IMAP_SEARCH_SUBJECT = process.env.MAGIC_LOGIN_IMAP_SEARCH_SUBJECT
  // global env
  const IMAP_SEARCH_SINCE_DATE = process.env.IMAP_SEARCH_SINCE_DATE
  const EMAIL_SEARCH_API_HOST = process.env.EMAIL_SEARCH_API_HOST

  const data = JSON.stringify({
    email_host: SHOP_OWNER_EMAIL_HOST,
    email_user: SHOP_OWNER_EMAIL_USER,
    email_password: SHOP_OWNER_EMAIL_PASSWORD,
    imap_search_subject: MAGIC_LOGIN_IMAP_SEARCH_SUBJECT,
    imap_search_unseen: IMAP_SEARCH_UNSEEN,
    imap_search_since_date: IMAP_SEARCH_SINCE_DATE
  })


  const options = {
    hostname: EMAIL_SEARCH_API_HOST,
    port: 443,
    path: '/search-email',
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Content-Length': data.length
    }
  }

  const req = https.request(options, res => {
    console.log(`statusCode: ${res.statusCode}`)
    if ( res.statusCode != 200 ) {
      console.error("Non 200 statusCode received");
      process.exit(-5);
    }
    res.on('data', resp => {
      process.stdout.write(resp)
      const emails = JSON.parse(resp.toString())
      if ( emails.length == 0 ) {
        console.error("Zero emails were returned.")
        process.exit(5)
      }
      const lastEmail = emails[emails.length -1]['email_body']
      if ( lastEmail.includes('/auth/login/') ) {
        const jsonToString = JSON.stringify(lastEmail);
        const regex = /"(http.*)(?:\\")/gm;
        const magic_login_url = regex.exec(jsonToString)[1];
        module.exports.magic_login_url = magic_login_url;
        return true
      } else {
        console.error("Could not find login text in email")
        process.exit(5)
      }
    })
  })

  req.on('error', error => {
    console.error(error)
  })

  req.write(data)
  req.end()
}

exports.checkShopOwnerLogin = checkShopOwnerLogin;

