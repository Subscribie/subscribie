import uuid
from unittest.mock import patch
from subscribie.models import Plan, Person, Subscription, PlanRequirements, database
from subscribie.settings import settings


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
        assert (
            call_kwargs["payment_intent_data"]["application_fee_amount"] == expected_fee
        )


def test_subscription_application_fee_percent_calculation(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that stripe_create_checkout_session calculates effective application_fee_percent
    including SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE + SUBSCRIBIE_FIXED_FEE_PENCE_INT fixed fee,
    and does NOT pass payment_intent_data in subscription mode.
    """
    interval_amount = 599
    sell_price = 0

    person = Person(
        email="subscriber@example.com",
        given_name="Sub",
        family_name="Scriber",
        uuid=str(uuid.uuid4()),
    )
    database.session.add(person)

    req = PlanRequirements(instant_payment=False, subscription=True)
    database.session.add(req)

    # 599p recurring weekly interval
    plan = Plan(
        title="Weekly Soap",
        uuid=str(uuid.uuid4()),
        sell_price=sell_price,
        interval_amount=interval_amount,
        interval_unit="week",
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

    SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE = settings.get(
        "SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE"
    )
    SUBSCRIBIE_FIXED_FEE_PENCE_INT = settings.get("SUBSCRIBIE_FIXED_FEE_PENCE_INT")
    # Target fee example: If SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE was 0.025 and
    # SUBSCRIBIE_FIXED_FEE_PENCE_INT was 40:
    # int(interval_amount * SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE) + SUBSCRIBIE_FIXED_FEE_PENCE_INT = 14 + 40 = 54
    # Effective percent: round((54 / 599) * 100, 2) = 9.02
    expected_fee_percent = round(
        (
            (
                int(interval_amount * SUBSCRIBIE_APPLICATION_FEE_DECIMAL_PERCENTAGE)
                + SUBSCRIBIE_FIXED_FEE_PENCE_INT
            )
            / interval_amount
        )
        * 100,
        2,
    )

    with client.session_transaction() as sess:
        sess["email"] = person.email
        sess["person_id"] = person.id
        sess["plan"] = plan.uuid
        sess["is_donation"] = False
        sess["subscribie_checkout_session_id"] = checkout_session_id

    with patch(
        "subscribie.blueprints.checkout.stripe.checkout.Session.create"
    ) as mock_session_create:
        mock_session_create.return_value.id = "cs_test_sub_789"

        response = client.post(
            "/stripe-create-checkout-session",
            json={"account_id": "acct_1TestConnectAccount"},
            content_type="application/json",
        )

        assert response.status_code == 200
        call_kwargs = mock_session_create.call_args[1]

        # Mode must be subscription
        assert call_kwargs["mode"] == "subscription"
        # Must NOT pass payment_intent_data in subscription mode (violation of Stripe api)
        assert "payment_intent_data" not in call_kwargs
        # subscription_data must contain calculated application_fee_percent
        assert (
            call_kwargs["subscription_data"]["application_fee_percent"]
            == expected_fee_percent
        )


def test_subscription_with_instant_payment_does_not_pass_payment_intent_data(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that a plan with both subscription and instant_payment (upfront fee)
    does not pass payment_intent_data to Stripe checkout in subscription mode.
    """
    person = Person(
        email="subscriber2@example.com",
        given_name="Sub",
        family_name="Scriber",
        uuid=str(uuid.uuid4()),
    )
    database.session.add(person)

    req = PlanRequirements(instant_payment=True, subscription=True)
    database.session.add(req)

    # 100p upfront + 599p recurring weekly
    plan = Plan(
        title="Hair Gel With Upfront",
        uuid=str(uuid.uuid4()),
        sell_price=100,
        interval_amount=599,
        interval_unit="week",
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
        mock_session_create.return_value.id = "cs_test_sub_upfront_101"

        response = client.post(
            "/stripe-create-checkout-session",
            json={"account_id": "acct_1TestConnectAccount"},
            content_type="application/json",
        )

        assert response.status_code == 200
        call_kwargs = mock_session_create.call_args[1]

        assert call_kwargs["mode"] == "subscription"
        assert "payment_intent_data" not in call_kwargs
        assert "subscription_data" in call_kwargs
        assert call_kwargs["subscription_data"]["application_fee_percent"] == 9.02
