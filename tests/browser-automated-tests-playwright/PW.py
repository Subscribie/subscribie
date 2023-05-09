from graphlib import TopologicalSorter
import time
import subprocess
import asyncio

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
    "452_shop_owner_categories_creation": [],
    "334_shop_owner_private_page_creation": [],
    "121_shop_owner_public_page_creation": [],
    "212_shop_owner_slogan_creation": [],
    "387_shop_owner_change_shop_colour": [],
    "463_shop_owner_adding_vat": [],
    "1_stripe_connect": [],
    "133_shop_owner_plan_creation": [],
    "275_shop_owner_changing_plans_order": [],
    "491_shop_owner_share_private_plan_url": [],
    "463_subscriber_ordering_plan_with_VAT": [
        "1_stripe_connect",
        "463_shop_owner_adding_vat",
    ],
    "475_subscriber_order_plan_with_free_trial": ["1_stripe_connect"],
    "264_subscriber_order_plan_with_choice_options_and_required_note": [
        "1_stripe_connect",
        "133_shop_owner_plan_creation",
    ],
    "516_subscriber_order_plan_with_cancel_at": [
        "1_stripe_connect",
        "133_shop_owner_plan_creation",
    ],
    "133_subscriber_order_plan_with_cooling_off": [
        "1_stripe_connect",
        "133_shop_owner_plan_creation",
    ],
    "293-1_subscriber_order_plan_with_only_recurring_charge": ["1_stripe_connect"],
    "293-2_subscriber_order_plan_with_only_upfront_charge": ["1_stripe_connect"],
    "293-3_subscriber_order_plan_with_recurring_and_upfront_charge": [
        "1_stripe_connect"
    ],
    "623_subscriber_magic_login": [
        "293-3_subscriber_order_plan_with_recurring_and_upfront_charge"
    ],
    "993_subscriber_change_card_details": [
        "293-3_subscriber_order_plan_with_recurring_and_upfront_charge"
    ],
    "619_shop_owner_transaction_filter_by_name_and_by_plan_title": [
        "293-3_subscriber_order_plan_with_recurring_and_upfront_charge"
    ],
    "905-subscriber-search-by-email-and-name": [
        "293-3_subscriber_order_plan_with_recurring_and_upfront_charge"
    ],
    "147_shop_owner_pause_resume_and_cancel_subscriptions": [
        "293-3_subscriber_order_plan_with_recurring_and_upfront_charge"
    ],
    "872_uploading_plan_picture": [],
    "1065_shop_owner_enabling_donations": [],
    "1065_subscriber_checkout_donation": [
        "1065_shop_owner_enabling_donations",
        "133_shop_owner_plan_creation",
    ],
    "1005_shop_owner_terms_and_conditions_creation": [
        "475_subscriber_order_plan_with_free_trial",
        "133_shop_owner_plan_creation",
    ],
    "1005_subscriber_terms_and_condition_check_test": [
        "939_subscriber_order_free_plan_with_terms_and_conditions"
    ],
    "939_subscriber_order_free_plan_with_terms_and_conditions": [
        "1005_shop_owner_terms_and_conditions_creation"
    ],
}

ts = TopologicalSorter(graph)


def test(ts):
    ts.prepare()
    while ts.is_active():
        node_group = ts.get_ready()
        yield node_group
        ts.done(*node_group)


async def run_test(tests):
    test_parts = tests.split("_")
    test_number = test_parts[0]
    test_type = test_parts[1]
    # Running the tests in the background while getting the stdout for debuggin purpose
    proc = await asyncio.create_subprocess_exec(
        f"npx playwright test --grep @{test_number}@{test_type} --update-snapshots",
        shell=False,
        stdout=subprocess.PIPE,
    )

    stdout = await proc.communicate()
    return stdout


async def main(tests):
    for group in test(ts):
        task = [asyncio.create_task(run_test(tests)) for tests in group]
        # waiting for all the background tasks
        results = await asyncio.gather(*task)
        # printing the output
        for i, result in enumerate(results):
            stdout = result
            print(f"Command {i+1} stdout: {stdout.decode().strip()}")
    # waiting 1min to wait for the tests to finishing before getting to depend tests
    time.sleep(60)


loop = asyncio.get_event_loop()
loop.run_until_complete(main(test(ts)))
