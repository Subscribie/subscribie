---
title: "Subscribie Payment Errors and Decline Codes"
date: 2023-09-12
weight: 5
description: >
  Learn the Payment Error and Decline Codes that are shown in Payment Retry Attempt Email
---

This is the complete list of potential error codes you may see when a payment collection fails, and an explanation of their reason. These errors are shown in the Subscriber view in Subscribie's dashboard and in Payment Retry Attempt Emails.

**authentication_required**
The card was declined as the transaction requires authentication. The customer should try again and authenticate their card when prompted during the transaction. If the card issuer returns this decline code on an authenticated transaction, the customer needs to contact their card issuer for more information.

**approve_with_id**
The payment can’t be authorized. Attempt the payment again. If you still can’t process it, the customer needs to contact their card issuer.

**call_issuer**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**card_not_supported**
The card does not support this type of purchase. The customer needs to contact their card issuer to make sure their card can be used to make this type of purchase.

**card_velocity_exceeded**
The customer has exceeded the balance, credit limit, or transaction amount limit available on their card. The customer needs to contact their card issuer for more information.

**currency_not_supported**
The card does not support the specified currency. The customer needs to check with the issuer whether the card can be used for the type of currency specified.

**do_not_honor**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**do_not_try_again**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**duplicate_transaction**
A transaction with an identical amount and credit card information was submitted very recently. Check to see if a recent payment already exists.

**expired_card**
The card has expired. The customer needs to use another card.

**fraudulent**
The payment was declined because Stripe suspects that it’s fraudulent. Don’t report more detailed information to your customer. Instead, present as you would the generic_decline described below.

**generic_decline**
The card was declined for an unknown reason or Stripe Radar blocked the payment. The customer needs to contact their card issuer for more information.

**incorrect_number**
The card number is incorrect. The customer needs to try again using the correct card number.

**incorrect_cvc**
The CVC number is incorrect. The customer needs to try again using the correct CVC.

**incorrect_pin**
The PIN entered is incorrect. This decline code only applies to payments made with a card reader. The customer needs to try again using the correct PIN.

**incorrect_zip**
The postal code is incorrect. The customer needs to try again using the correct billing postal code.

**insufficient_funds**
The card has insufficient funds to complete the purchase. The customer needs to use an alternative payment method.

**invalid_account**
The card, or account the card is connected to, is invalid. The customer needs to contact their card issuer to check that the card is working correctly.

**invalid_amount**
The payment amount is invalid or exceeds the amount that’s allowed. If the amount appears to be correct, the customer needs to check with their card issuer that they can make purchases of that amount.

**invalid_cvc**
The CVC number is incorrect. The customer needs to try again using the correct CVC.

**invalid_expiry_month**
The expiration month is invalid. The customer needs to try again using the correct expiration date.

**invalid_expiry_year**
The expiration year is invalid. The customer needs try again using the correct expiration date.

**invalid_number**
The card number is incorrect. The customer needs try again using the correct card number.

**invalid_pin**
The PIN entered is incorrect. The customer needs to try again using the correct PIN.

**issuer_not_available**
The card issuer couldn’t be reached, so the payment couldn’t be authorized. Attempt the payment again. If you still can’t process it, the customer needs to contact their card issuer.

**lost_card**
The payment was declined because the card is reported lost. The specific reason for the decline shouldn’t be reported to the customer. Instead, it needs to be presented as a generic decline.

**merchant_blacklist**
The payment was declined because it matches a value on the Stripe user’s block list. Don’t report more detailed information to your customer. Instead, present as you would the generic_decline described above.

**new_account_information_available**
The card, or account the card is connected to, is invalid. The customer needs to contact their card issuer for more information.

**no_action_taken**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**not_permitted**
The payment isn’t permitted. The customer needs to contact their card issuer for more information.

**offline_pin_required**
The card was declined because it requires a PIN. The customer needs to try again by inserting their card and entering a PIN.

**online_or_offline_pin_required**
The card was declined as it requires a PIN. If the card reader supports Online PIN, prompt the customer for a PIN without creating a new transaction. If the card reader doesn’t support Online PIN, the customer needs to try again by inserting their card and entering a PIN.

**pickup_card**
The customer can’t use this card to make this payment (it’s possible it was reported lost or stolen). They need to contact their card issuer for more information.

**pin_try_exceeded**
The allowable number of PIN tries was exceeded. The customer must use another card or method of payment.

**processing_error**
An error occurred while processing the card. The payment needs to be attempted again. If it still can’t be processed, try again later.

**reenter_transaction**
The payment couldn’t be processed by the issuer for an unknown reason. The payment needs to be attempted again. If it still can’t be processed, the customer needs to contact their card issuer.

**restricted_card**
The customer can’t use this card to make this payment (it’s possible it was reported lost or stolen). The customer needs to contact their card issuer for more information.

**revocation_of_all_authorizations**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**revocation_of_authorization**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**security_violation**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**service_not_allowed**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**stolen_card**
The payment was declined because the card is reported stolen. The specific reason for the decline shouldn’t be reported to the customer. Instead, it needs to be presented as a generic decline.

**stop_payment_order**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**testmode_decline**
A Stripe test card number was used. A genuine card must be used to make a payment.

**transaction_not_allowed**
The card was declined for an unknown reason. The customer needs to contact their card issuer for more information.

**try_again_later**
The card was declined for an unknown reason. Ask the customer to attempt the payment again. If subsequent payments are declined, the customer needs to contact their card issuer for more information.

**withdrawal_count_limit_exceeded**
The customer has exceeded the balance or credit limit available on their card. The customer needs to use an alternative payment method.

**What happens to failed payments?**
Failed payments are retried for a default of 4 times. In case a payment fails you will receive a notification email, stating the reason for the failed payment. Learn more about the process of failing payments and [how they are retried by Subscribie here.](https://docs.subscribie.co.uk/docs/tasks/view-failed-payments/)