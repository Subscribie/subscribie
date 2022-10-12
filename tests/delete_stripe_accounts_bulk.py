import stripe
import os
import json

"""
Config:

KEEP_SHOPS_LIST is stored in amber.yaml
The password for that is stored in the password vault

- Install amber https://github.com/fpco/amber/releases

USAGE:

export AMBER_SECRET=stored-in-password-fault

amber exec -v -- python3 -i delete_stripe_accounts_bulk.py 

"""

STRIPE_API_KEY = os.getenv("STRIPE_TEST_SECRET_KEY")
stripe.api_key = STRIPE_API_KEY

keep_shops_list = json.loads(os.getenv("KEEP_SHOPS_LIST"))
paginate_limit_number = os.getenv("paginate_limit_number", 100)

assert type(keep_shops_list) is list
assert len(keep_shops_list) > 0


accounts = stripe.Account.list(limit=paginate_limit_number)
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
                if account.id not in keep_shops_list:
                    result = stripe.Account.delete(account.id)
                    print(result)
            except stripe.error.InvalidRequestError as error:
                print(error)
    except Exception as error:
        print(error)
print("All test shops deleted")
