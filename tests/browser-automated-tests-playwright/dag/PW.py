from graphlib import TopologicalSorter

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
    "clear-db": [],
    "categories-creation": [],
    "private-page-creation": [],
    "public-page-creation": [],
    "slogan-creation": [],
    "change-shop-colour": [],
    "adding-vat": [],
    "stripe-connect": [],
    "plan-creation": [],
    "changing-plan-order": [],
    "share-private-plan-url": [],
    "ordering-plan-with-vat": ["stripe-connect", "adding-vat"],
    "ordering-free-plan": ["stripe-connect"],
    "ordering-plan-with-choice-options-and-required-note": [
        "stripe-connect",
        "plan-creation",
    ],
    "ordering-plan-with-cancel-at": ["stripe-connect", "plan-creation"],
    "ordering-plan-cooling-off": ["stripe-connect", "plan-creation"],
    "ordering-plan-with-only-recurring-charge": ["stripe-connect"],
    "ordering-plan-with-only-upfront-charge": ["stripe-connect"],
    "ordering-plan-with-free-trial": ["stripe-connect"],
    "ordering-plan-with-subscription-and-upfront-charge": ["stripe-connect"],
    "subscriber-magic-login": ["ordering-plan-with-subscription-and-upfront-charge"],
    "subscriber-change-card-detauls": [
        "ordering-plan-with-subscription-and-upfront-charge"
    ],
    "transaction-filter-by-name-and-plan-title": [
        "ordering-plan-with-subscription-and-upfront-charge"
    ],
    "subscriber-filter-by-name-and-plan-title": [
        "ordering-plan-with-subscription-and-upfront-charge"
    ],
    "pause-resume-and-cancel-subscription": [
        "ordering-plan-with-subscription-and-upfront-charge"
    ],
    "uploading-a-plan-picture": [],
    "enabling-donations": [],
    "checkout-donation": ["enabling-donations", "stripe-connect"],
    "terms-and-conditions-creation": ["ordering-free-plan","plan-creation"],
    "terms-and-conditions-check-test": ["terms-and-conditions-creation"]
    }

ts = TopologicalSorter(graph)


def test(ts):
    ts.prepare()
    while ts.is_active():
        node_group = ts.get_ready()
        yield node_group
        ts.done(*node_group)


for group in test(ts):

    print(group)
