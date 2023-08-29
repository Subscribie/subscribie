const https = require('https');

function checkNewSubscriberEmail() {
  console.log("executing checkNewSubscriberEmail");
  const SUBSCRIBER_EMAIL_HOST = process.env.SUBSCRIBER_EMAIL_HOST
  const SUBSCRIBER_EMAIL_USER = process.env.SUBSCRIBER_EMAIL_USER
  const SUBSCRIBER_EMAIL_PASSWORD = process.env.SUBSCRIBER_EMAIL_PASSWORD
  const IMAP_SEARCH_UNSEEN = parseInt(process.env.IMAP_SEARCH_UNSEEN)
  const NEW_SUBSCRIBER_IMAP_SEARCH_SUBJECT = process.env.NEW_SUBSCRIBER_IMAP_SEARCH_SUBJECT
  // global env
  const IMAP_SEARCH_SINCE_DATE = process.env.IMAP_SEARCH_SINCE_DATE
  const EMAIL_SEARCH_API_HOST = process.env.EMAIL_SEARCH_API_HOST

  const data = JSON.stringify({
    email_host: SUBSCRIBER_EMAIL_HOST,
    email_user: SUBSCRIBER_EMAIL_USER,
    email_password: SUBSCRIBER_EMAIL_PASSWORD,
    imap_search_subject: NEW_SUBSCRIBER_IMAP_SEARCH_SUBJECT,
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
        console.error("Zero emails were returned.");
        process.exit(5);
      }
      const lastEmail = emails[emails.length -1]['email_body']
      if ( lastEmail.includes('You have a new subscriber!')) {
        const jsonToString = JSON.stringify(lastEmail);
        const regex = /Subscriber Name: (.*)(?:\\r)/gm;
        const subscriber_name = regex.exec(jsonToString)[1];
        console.log(subscriber_name)
        module.exports.subscriber_name = subscriber_name;
        return true
      } else {
        console.error("Could not find login text in email");
        process.exit(5);
      }
    })
  })

  req.on('error', error => {
    console.error(error)
  })

  req.write(data)
  req.end()
}
exports.checkNewSubscriberEmail = checkNewSubscriberEmail;

