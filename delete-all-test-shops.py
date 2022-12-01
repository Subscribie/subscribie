import stripe
import os

STRIPE_API_KEY = os.getenv("STRIPE_TEST_SECRET_KEY")
stripe.api_key = STRIPE_API_KEY

accounts = stripe.Account.list(limit=100)
for account in accounts.auto_paging_iter():
    try:
        if (
            "Soap Subscription" in account.business_profile.name
            or "Business Name" in account.business_profile.name
        ):
            # If we get here, then it's a test Stripe account
            # which we can safley delete
            print(account)
            try:
                result = stripe.Account.delete(account.id)
                print(result)
            except stripe.error.InvalidRequestError as error:
                print(error)
    except Exception as error:
        print(error)
print("All test shops deleted")
