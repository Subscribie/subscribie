import uuid
from unittest.mock import patch
from subscribie.models import Plan, Person, Subscription, PlanRequirements, database


def test_subscription_checkout_calculates_fee_percent_with_fixed_fee(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that stripe_create_checkout_session calculates application_fee_percent
    on subscription_data to include the 2.5% + 40p fee for initial subscription cycle.
    """
    person = Person(
        email="sub_buyer@example.com",
        given_name="Sub",
        family_name="Buyer",
        uuid=str(uuid.uuid4()),
    )
    database.session.add(person)

    req = PlanRequirements(instant_payment=False, subscription=True)
    database.session.add(req)

    # 1000 pence (£10.00) recurring interval amount
    # Fee: int(1000 * 0.025) + 40 = 25 + 40 = 65p
    # Percentage: round((65 / 1000) * 100, 2) = 6.5
    plan = Plan(
        title="Monthly Coffee Plan",
        uuid=str(uuid.uuid4()),
        sell_price=0,
        interval_amount=1000,
        interval_unit="month",
        requirements=req,
    )
    database.session.add(plan)

    checkout_session_id = str(uuid.uuid4())
    sub = Subscription(
        uuid=str(uuid.uuid4()),
        person=person,
        plan=plan,
        subscribie_checkout_session_id=checkout_session_id,
    )
    database.session.add(sub)
    database.session.commit()

    with client.session_transaction() as sess:
        sess["email"] = person.email
        sess["person_id"] = person.id
        sess["plan"] = plan.uuid
        sess["is_donation"] = False
        sess["subscribie_checkout_session_id"] = checkout_session_id

    with patch(
        "subscribie.blueprints.checkout.stripe.checkout.Session.create"
    ) as mock_session_create:
        mock_session_create.return_value.id = "cs_test_sub_123"

        response = client.post(
            "/stripe-create-checkout-session",
            json={"account_id": "acct_1TestConnectAccount"},
            content_type="application/json",
        )

        assert response.status_code == 200
        call_kwargs = mock_session_create.call_args[1]
        assert "subscription_data" in call_kwargs
        subscription_data = call_kwargs["subscription_data"]
        # Expected fee percent is 6.5%
        assert subscription_data["application_fee_percent"] == 6.5
