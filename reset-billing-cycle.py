import stripe

# Set your secret key. Remember to switch to your live secret key in production.
# See your keys here: https://dashboard.stripe.com/apikeys
stripe.api_key = "sk_test_xxxxxxxxxxxx"

# the code below, charge the subscription the full amount of the subscription
# immediately without waiting for the next payment date
subscription = stripe.Subscription.modify(
    "sub_xxxxxxxxxxxxx",
    billing_cycle_anchor="now",
    proration_behavior="none",
    stripe_account="acct_xxxxxxx",
)
