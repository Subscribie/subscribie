const https = require('https');

function checkSubscriberLogin() {
  subscriber_email_host = process.env.subscriber_email_host
  subscriber_email_user = process.env.subscriber_email_user
  subscriber_email_password = process.env.subscriber_email_password
  reset_password_imap_search_subject = process.env.reset_password_imap_search_subject
  imap_search_unseen = process.env.imap_search_unseen
  imap_search_since_date = process.env.imap_search_since_date

  email_search_api_host = process.env.email_search_api_host

  const data = JSON.stringify({
    email_host: subscriber_email_host,
    email_user: subscriber_email_user,
    email_password: subscriber_email_password,
    imap_search_subject: reset_password_imap_search_subject,
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
    if ( res.statusCode != 200 ) {
      console.error("Non 200 statusCode received");
      process.exit(-5);
    }
    res.on('data', resp => {
      process.stdout.write(resp)
      emails = JSON.parse(resp.toString())
      if ( emails.length == 0 ) {
        console.error("Zero emails were returned.")
        process.exit(5)
      }
      lastEmail = emails[emails.length -1]['email_body']
      if ( lastEmail.includes('/account/password-reset')) {
        //json to string
        jsonToString = JSON.stringify(lastEmail);

        // filter email magic login url
        const regex = /"(http.*)(?:\\r)/gm;
        reset_password_url = regex.exec(jsonToString)[1];
        module.exports.reset_password_url = reset_password_url;
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
exports.checkSubscriberLogin = checkSubscriberLogin;

