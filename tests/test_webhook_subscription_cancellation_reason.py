"""Regression tests for issue #1466.

Issue: https://github.com/Subscribie/subscribie/issues/1466

When Stripe sends a ``customer.subscription.deleted`` webhook, the
``cancellation_details.reason`` it carries (e.g. ``payment_failed``,
``cancellation_requested``) must be persisted onto the local
``Subscription.stripe_cancellation_reason`` column, so the shop owner can
see *why* a subscription was cancelled from the subscribers UI.
"""

import json
from unittest.mock import patch

from subscribie.database import database
from subscribie.models import Company, Person, Plan, Subscription


def _ensure_company():
    if Company.query.first() is None:
        company = Company()
        company.name = "Test Shop"
        database.session.add(company)
        database.session.commit()


def _make_subscription(checkout_session_id, stripe_subscription_id):
    _ensure_company()
    person = Person(
        given_name="Ada",
        family_name="Lovelace",
        email="ada@example.com",
        uuid=f"person-uuid-1466-{stripe_subscription_id}",
    )
    database.session.add(person)
    plan = Plan(
        title="Monthly Widget",
        uuid=f"plan-uuid-1466-{stripe_subscription_id}",
    )
    database.session.add(plan)
    database.session.commit()

    subscription = Subscription(
        sku_uuid=plan.uuid,
        person_id=person.id,
        stripe_subscription_id=stripe_subscription_id,
        subscribie_checkout_session_id=checkout_session_id,
        stripe_status="active",
    )
    database.session.add(subscription)
    database.session.commit()
    return subscription, person, plan


def _build_event(
    checkout_session_id, stripe_subscription_id, reason, person_uuid, plan_uuid
):
    return {
        "livemode": False,
        "type": "customer.subscription.deleted",
        "account": "acct_1TestConnectAccount",
        "data": {
            "object": {
                "id": stripe_subscription_id,
                "status": "canceled",
                "ended_at": 1700000000,
                "cancellation_details": {"reason": reason},
                "metadata": {
                    "subscribie_checkout_session_id": checkout_session_id,
                    "person_uuid": person_uuid,
                    "plan_uuid": plan_uuid,
                },
            }
        },
    }


def test_customer_subscription_deleted_persists_payment_failed_reason(
    client,
    app,
    db_session,
    with_shop_owner,
    with_default_country_code_and_default_currency,
):
    subscription, person, plan = _make_subscription(
        checkout_session_id="cs_1466_pf",
        stripe_subscription_id="sub_1466_pf",
    )

    payload = _build_event(
        checkout_session_id=subscription.subscribie_checkout_session_id,
        stripe_subscription_id=subscription.stripe_subscription_id,
        reason="payment_failed",
        person_uuid=person.uuid,
        plan_uuid=plan.uuid,
    )

    with patch(
        "subscribie.blueprints.checkout.PaymentProvider"
    ) as payment_provider_cls:
        payment_provider_cls.query.first.return_value.stripe_livemode = False
        response = client.post(
            "/stripe_webhook",
            data=json.dumps(payload),
            content_type="application/json",
        )

    assert response.status_code == 200

    refreshed = Subscription.query.filter_by(uuid=subscription.uuid).one()
    assert refreshed.stripe_cancellation_reason == "payment_failed"
    assert refreshed.stripe_status == "canceled"
    assert refreshed.stripe_ended_at == 1700000000


def test_customer_subscription_deleted_persists_cancellation_requested_reason(
    client,
    app,
    db_session,
    with_shop_owner,
    with_default_country_code_and_default_currency,
):
    subscription, person, plan = _make_subscription(
        checkout_session_id="cs_1466_cr",
        stripe_subscription_id="sub_1466_cr",
    )

    payload = _build_event(
        checkout_session_id=subscription.subscribie_checkout_session_id,
        stripe_subscription_id=subscription.stripe_subscription_id,
        reason="cancellation_requested",
        person_uuid=person.uuid,
        plan_uuid=plan.uuid,
    )

    with patch(
        "subscribie.blueprints.checkout.PaymentProvider"
    ) as payment_provider_cls:
        payment_provider_cls.query.first.return_value.stripe_livemode = False
        response = client.post(
            "/stripe_webhook",
            data=json.dumps(payload),
            content_type="application/json",
        )

    assert response.status_code == 200

    refreshed = Subscription.query.filter_by(uuid=subscription.uuid).one()
    assert refreshed.stripe_cancellation_reason == "cancellation_requested"
    assert refreshed.stripe_status == "canceled"
