import uuid
from unittest.mock import patch
from subscribie.models import Plan, Person, Subscription, PlanRequirements, database


def test_instant_payment_application_fee_calculation(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that stripe_create_checkout_session calculates 2.5% + 40p
    application fee for instant payment plans.
    """
    # 1. Create a person
    person = Person(
        email="buyer@example.com",
        given_name="Test",
        family_name="Buyer",
        uuid=str(uuid.uuid4()),
    )
    database.session.add(person)

    # 2. Create requirement with instant payment
    req = PlanRequirements(instant_payment=True, subscription=False)
    database.session.add(req)

    # 3. Create plan with sell_price = 2000 pence (£20.00)
    plan = Plan(
        title="Instant Plan",
        uuid=str(uuid.uuid4()),
        sell_price=2000,
        interval_amount=0,
        requirements=req,
    )
    database.session.add(plan)

    # 4. Create subscription tracking object
    checkout_session_id = str(uuid.uuid4())
    sub = Subscription(
        uuid=str(uuid.uuid4()),
        person=person,
        plan=plan,
        subscribie_checkout_session_id=checkout_session_id,
    )
    database.session.add(sub)
    database.session.commit()

    # Expected fee: int(2000 * 0.025) + 40 = 50 + 40 = 90
    expected_fee = 90

    with client.session_transaction() as sess:
        sess["email"] = person.email
        sess["person_id"] = person.id
        sess["plan"] = plan.uuid
        sess["is_donation"] = False
        sess["subscribie_checkout_session_id"] = checkout_session_id

    with patch(
        "subscribie.blueprints.checkout.stripe.checkout.Session.create"
    ) as mock_session_create:
        mock_session_create.return_value.id = "cs_test_instant_123"

        response = client.post(
            "/stripe-create-checkout-session",
            json={"account_id": "acct_1TestConnectAccount"},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert mock_session_create.called
        call_kwargs = mock_session_create.call_args[1]

        assert "payment_intent_data" in call_kwargs
        payment_intent_data = call_kwargs["payment_intent_data"]
        assert payment_intent_data["application_fee_amount"] == expected_fee


def test_instant_payment_application_fee_capped_at_total(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that application_fee_amount cannot exceed sell_price for small instant payments.
    """
    person = Person(
        email="buyer2@example.com",
        given_name="Small",
        family_name="Buyer",
        uuid=str(uuid.uuid4()),
    )
    database.session.add(person)

    req = PlanRequirements(instant_payment=True, subscription=False)
    database.session.add(req)

    # 30p sell_price
    plan = Plan(
        title="Micro Plan",
        uuid=str(uuid.uuid4()),
        sell_price=30,
        interval_amount=0,
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

    # Fee raw: int(30 * 0.025) + 40 = 40, capped at 30
    expected_fee = 30

    with client.session_transaction() as sess:
        sess["email"] = person.email
        sess["person_id"] = person.id
        sess["plan"] = plan.uuid
        sess["is_donation"] = False
        sess["subscribie_checkout_session_id"] = checkout_session_id

    with patch(
        "subscribie.blueprints.checkout.stripe.checkout.Session.create"
    ) as mock_session_create:
        mock_session_create.return_value.id = "cs_test_instant_456"

        response = client.post(
            "/stripe-create-checkout-session",
            json={"account_id": "acct_1TestConnectAccount"},
            content_type="application/json",
        )

        assert response.status_code == 200
        call_kwargs = mock_session_create.call_args[1]
        assert call_kwargs["payment_intent_data"]["application_fee_amount"] == expected_fee
