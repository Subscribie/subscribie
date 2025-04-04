#!/bin/env python3

from graphlib import TopologicalSorter
from graphviz import Digraph
import subprocess
from multiprocessing import Manager, Pool


graph = {
    "@stripe_connect": [],
    "@475_shop_owner_create_free_plan_with_question_attached": [
        "@1333_shop_owner_add_free_text_question"
    ],
    "@1333-1_subscriber_order_free_plan_with_question_attached": [
        "@1333_shop_owner_add_free_text_question",
        "@475_shop_owner_create_free_plan_with_question_attached",
    ],
    "@452_shop_owner_create_category": [
        "@475_subscriber_order_plan_with_free_trial",
        "@264_subscriber_order_plan_with_choice_options_and_required_note",
        "@133_subscriber_order_plan_with_cooling_off_period",
        "@293_subscriber_order_recurring_plan",
        "@293-2_subscriber_order_plan_with_only_upfront_charge",
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge",
        "@939_subscriber_order_free_plan_with_terms_and_conditions",
        "@516_subscriber_order_plan_with_cancel_at",
    ],
    "@121_shop-owner-create-public-page": [],
    "@212_shop_owner_slogan_creation": [],
    "@387_shop_owner_change_shop_colour": [],
    "@463_shop_owner_adding_vat": [
        "@475_subscriber_order_plan_with_free_trial",
        "@264_subscriber_order_plan_with_choice_options_and_required_note",
        "@133_subscriber_order_plan_with_cooling_off_period",
        "@293_subscriber_order_recurring_plan",
        "@293-2_subscriber_order_plan_with_only_upfront_charge",
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge",
        "@939_subscriber_order_free_plan_with_terms_and_conditions",
        "@516_subscriber_order_plan_with_cancel_at",
    ],
    "@133_shop_owner_plan_creation": ["@334-shop-owner-create-private-page"],
    "@264_shop_owner_create_plan_with_choice_options": [
        "@130-1_shop_owner_can_create_choice_options"
    ],
    "@275_shop_owner_change_plan_order": [
        "@133_shop_owner_plan_creation",
        "@475_shop_owner_create_free_trial",
        "@516_shop_owner_create_cancel_at_plan",
        "@491_shop_owner_create_private_plan",
        "@264_shop_owner_create_plan_with_choice_options",
        "@130-1_shop_owner_can_create_choice_options",
    ],
    "@1219_shop-owner_enable_custom_url": [
        "@463_subscriber_order_plan_with_vat",
        "@475_subscriber_order_plan_with_free_trial",
        "@264_subscriber_order_plan_with_choice_options_and_required_note",
        "@133_subscriber_order_plan_with_cooling_off_period",
        "@293_subscriber_order_recurring_plan",
        "@293-2_subscriber_order_plan_with_only_upfront_charge",
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge",
        "@939_subscriber_order_free_plan_with_terms_and_conditions",
    ],
    "@264_subscriber_order_plan_with_choice_options_and_required_note": [
        "@stripe_connect",
        "@130-1_shop_owner_can_create_choice_options",
        "@264_shop_owner_create_plan_with_choice_options",
    ],
    "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge": [
        "@stripe_connect",
        "@293_subscriber_order_recurring_plan",
        "@475_subscriber_order_plan_with_free_trial",
        "@264_subscriber_order_plan_with_choice_options_and_required_note",
        "@133_subscriber_order_plan_with_cooling_off_period",
        "@293_subscriber_order_recurring_plan",
        "@293-2_subscriber_order_plan_with_only_upfront_charge",
        "@939_subscriber_order_free_plan_with_terms_and_conditions",
    ],
    "@463_subscriber_order_plan_with_vat": [
        "@stripe_connect",
        "@463_shop_owner_adding_vat",
    ],
    "@475_subscriber_order_plan_with_free_trial": [
        "@stripe_connect",
        "@475_shop_owner_create_free_trial",
        "@1005_shop_owner_terms_and_conditions_creation",
        "@293_subscriber_order_recurring_plan",
        "@264_subscriber_order_plan_with_choice_options_and_required_note",
        "@133_subscriber_order_plan_with_cooling_off_period",
        "@293_subscriber_order_recurring_plan",
        "@293-2_subscriber_order_plan_with_only_upfront_charge",
        "@939_subscriber_order_free_plan_with_terms_and_conditions",
    ],
    "@133_subscriber_order_plan_with_cooling_off_period": [
        "@stripe_connect",
        "@133_shop_owner_create_plan_with_cooling_off_period",
    ],
    "@293_subscriber_order_recurring_plan": [
        "@stripe_connect",
    ],
    "@293-2_subscriber_order_plan_with_only_upfront_charge": [
        "@stripe_connect",
    ],
    "@619_shop_owner_transaction_filter_by_name_and_by_plan_title": [
        "@stripe_connect",
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge",
    ],
    "@516_subscriber_order_plan_with_cancel_at": [
        "@stripe_connect",
        "@516_shop_owner_create_cancel_at_plan",
    ],
    "@905-subscriber-search-by-email-and-name": [
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge"
    ],
    "@147_shop_owner_pause_resume_and_cancel_subscriptions": [
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge"
    ],
    "@872_uploading_plan_picture": [],
    "@1005_shop_owner_terms_and_conditions_creation": [
        "@475_shop_owner_create_free_trial"
    ],
    "@1065_shop_owner_enabling_donations": [],
    "@1065_subscriber_checkout_donation": ["@1065_shop_owner_enabling_donations"],
    "@939_subscriber_order_free_plan_with_terms_and_conditions": [
        "@1005_shop_owner_terms_and_conditions_creation",
        "@stripe_connect",
    ],
    "1431_shop_owner_bulk_pause_payment_collection_all_subscribers": [
        "@293_subscriber_order_recurring_plan",
        "@264_subscriber_order_plan_with_choice_options_and_required_note",
        "@475_subscriber_order_plan_with_free_trial",
        "@293-3_subscriber_order_plan_with_weekly_recurring_and_upfront_charge",
        "@463_subscriber_order_plan_with_vat",
        "@1333-1_subscriber_order_free_plan_with_question_attached",
        "@133_subscriber_order_plan_with_cooling_off_period",
        "@293-2_subscriber_order_plan_with_only_upfront_charge",
    ],
}

# Visualise DAG
dot = Digraph()
for node in graph:
    dot.node(str(node))
    for child in graph[node]:
        dot.edge(str(node), str(child))

# Flick to True to open the graph in a viewer right away
dot.render("./graphviz_output.gv", view=False)


ts = TopologicalSorter(graph)


def test(ts):
    ts.prepare()
    while ts.is_active():
        node_group = ts.get_ready()
        yield node_group
        ts.done(*node_group)


# initialize worker processes
def init_worker(shared_event):
    # store the event as a global in the worker process
    global event
    event = shared_event


# Function to run a test based on it's name
def run_test(test_name: str):
    # check for stop event
    if event.is_set():
        print(
            f"Stopping test {test_name} because some other test raised an exception",
            flush=True,
        )
    else:
        print("#" * 80)
        print("Event is NOT set")
        print("#" * 80)
    print(f"Running test {test_name}")
    output_path = "./test-videos/" + test_name[1:]
    result = subprocess.run(
        # f"npx playwright test --grep {test_name} --headed --retries 0 --update-snapshots",  # noqa: E501
        f"npx playwright test --update-snapshots --grep '{test_name}' --output '{output_path}'",  # noqa: E501
        shell=True,
    )
    if result.returncode != 0:
        # cancel all other tests
        event.set()
        raise RuntimeError(
            f"Test {test_name} failed with return code {result.returncode}, {result}"
        )


print("Running tests as fast as possible")
for group in test(ts):
    # Use a multiprocessing Pool to run the test in parallel
    print(f"Starting to run tests {group} in parallel")
    with Manager() as manager:
        # create a shared event
        shared_event = manager.Event()
        # create and configure the process pool
        with Pool(
            processes=None, initializer=init_worker, initargs=(shared_event,)
        ) as pool:
            # issue tasks into the process pool
            result = pool.map(run_test, group)
