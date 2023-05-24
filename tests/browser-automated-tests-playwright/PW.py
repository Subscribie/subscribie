from graphlib import TopologicalSorter
import subprocess
import multiprocessing

"""

You might imagine that the unique numbers refer to tests.

This code automatically works out which tests can run in parallel

"""

# Note that graph values must be iterables (if you pass a
# string e.g. "333" that won't work because TopologicalSorter
# will treat that as "3", "3", and "3" ).
# To overcome that, put the values (depenants) as lists with single
# elements. e.g. ["333"]
graph = {
    "1_shop-owner_stripe-connect": [],
    "133_shop-owner_plan-creation": [],
    "452_shop-owner_categories-creation": [],
    "334_shop-owner_private-page-creation": [],
    "121_shop-owner_public-page-creation": [],
    "387_shop-owner_change-shop-colour": [],
    "212_shop-owner_slogan-creation": [],
    "463_shop-owner_adding-vat": ["1_shop-owner_stripe-connect"],
    "275_shop-owner_changing-plans-order": ["133_shop-owner_plan-creation"],
    "491_shop-owner_share-private-plan-url": ["133_shop-owner_plan-creation"],
    "463_subscriber_ordering-plan-with-VAT": [
        "1_shop-owner_stripe-connect",
        "463_shop-owner_adding-vat",
    ],
    "475_subscriber_order-plan-with-free-trial": [
        "1_shop-owner_stripe-connect",
        "133_shop-owner_plan-creation",
    ],
    "264_subscriber_order-plan-with-choice-options-and-required-note": [
        "1_shop-owner_stripe-connect",
        "133_shop-owner_plan-creation",
    ],
    "516_subscriber_order-plan-with-cancel-at": [
        "1_shop-owner_stripe-connect",
        "133_shop-owner_plan-creation",
    ],
    "133_subscriber_order-plan-with-cooling-off": [
        "1_shop-owner_stripe-connect",
        "133_shop-owner_plan-creation",
    ],
    "293-1_subscriber_order-plan-with-only-recurring-charge": [
        "1_shop-owner_stripe-connect"
    ],
    "293-2_subscriber_order-plan-with-only-upfront-charge": [
        "1_shop-owner_stripe-connect"
    ],
    "293-3_subscriber_order-plan-with-recurring-and-upfront-charge": [
        "1_shop-owner_stripe-connect"
    ],
    "623_subscriber_magic-login": [
        "293-3_subscriber_order-plan-with-recurring-and-upfront-charge"
    ],
    "993_subscriber_change-card-details": ["623_subscriber_magic-login"],
    "619_shop-owner_transaction-filter-by-name-and-by-plan-title": [
        "293-3_subscriber_order-plan-with-recurring-and-upfront-charge"
    ],
    "905_subscriber_search-by-email-and-name": [
        "293-3_subscriber_order-plan-with-recurring-and-upfront-charge"
    ],
    "147_shop-owner_pause-resume-and-cancel-subscriptions": [
        "293-3_subscriber_order-plan-with-recurring-and-upfront-charge"
    ],
    "872_shop-owner_uploading-plan-picture": [],
    "1065_shop-owner_enabling-donations": [],
    "1065_subscriber_checkout-donation": [
        "1065_shop-owner_enabling-donations",
        "133_shop-owner_plan-creation",
    ],
    "1005_shop-owner_terms-and-conditions-creation": [
        "475_subscriber_order-plan-with-free-trial",
        "133_shop-owner_plan-creation",
    ],
    "1005_subscriber_terms-and-condition-check-test": [
        "939_subscriber_order-free-plan-with-terms-and-conditions",
        "623_subscriber_magic-login",
    ],
    "939_subscriber_order-free-plan-with-terms-and-conditions": [
        "1005_shop-owner_terms-and-conditions-creation",
        "623_subscriber_magic-login",
    ],
}

ts = TopologicalSorter(graph)


def test(ts):
    ts.prepare()
    while ts.is_active():
        node_group = ts.get_ready()
        yield node_group
        ts.done(*node_group)


def run_test(tests):
    test_parts = tests.split("_")
    test_names = test_parts[2]
    # Running the tests in the background while getting the stdout for debuggin purpose
    print(f"Currently Running {test_parts}")
    subprocess.run(
        f"npx playwright test --grep @{test_names} --update-snapshots",
        shell=True,
    )


print("Test Are Running")


for group in test(ts):
    num_process = 6
    print("tests are starting")
    with multiprocessing.Pool(processes=num_process) as pool:
        pool.map(run_test, group)
