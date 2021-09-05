const https = require('https')

function checkShopOwnerLogin() {
  email_host = process.env.email_host
  email_user = process.env.email_user
  email_password = process.env.email_password
  imap_search_subject = process.env.imap_search_subject
  imap_search_unseen = process.env.imap_search_unseen
  imap_search_since_date = process.env.imap_search_since_date

  email_search_api_host = process.env.email_search_api_host

  const data = JSON.stringify({
    email_host: email_host,
    email_user: email_user,
    email_password: email_password,
    imap_search_subject: imap_search_subject,
    imap_search_unseen: imap_search_unseen,
    imap_search_since_date: imap_search_since_date
  })


  const options = {
    hostname: email_search_api_host,
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

    res.on('data', resp => {
      process.stdout.write(resp)
      emails = JSON.parse(resp.toString())
      if ( emails.length == 0 ) {
        console.error("Zero emails were returned.")
        process.exit(5)
      }
      lastEmail = emails[emails.length -1]['email_body']
      if ( lastEmail.includes('/auth/login/') ) {
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

