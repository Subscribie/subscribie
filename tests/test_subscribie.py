import pytest
from subscribie.models import User

from contextlib import contextmanager
from flask import appcontext_pushed, g


@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


def test_admin_can_view_dashboard(
    session, app, client, admin_session, with_default_country_code_and_default_currency
):
    user = User.query.filter_by(email="admin@example.com").first()
    with user_set(app, user):
        client.get("/admin/dashboard", follow_redirects=True)


def test_admin_can_add_plan(
    session, app, client, admin_session, with_default_country_code_and_default_currency
):
    user = User.query.filter_by(email="admin@example.com").first()
    with user_set(app, user):
        req = client.post(
            "/admin/add",
            follow_redirects=True,
            data={
                # TODO add plan should not use PlansForm as it requires company
                "company_name": "Coffee Castle",
                "slogan": "None",
                "email": "admin@example.com",
                "title-0": "Coffee Delux",
                "selling_points-0-0": "Roasted by us",
                "selling_points-0-1": "Monthly delievey",
                "selling_points-0-3": "Highest Quality",
                "description-0": "A long description",
                "image-0": "",
                "subscription-0": "yes",
                "interval_amount-0": "6.95",
                "interval_unit-0": "monthly",
                "days_before_first_charge-0": "0",
                "trial_period_days-0": "0",
                "instant_payment-0": "yes",
                "sell_price-0": "5",
                "note_to_buyer_message-0": "",
                "position-0": "",
            },
        )
        assert "Plan added." in req.data.decode("utf-8")

        # Verify plan has been stored correctly
        # by visiting admin edit plans page
        req = client.get("/admin/edit")

        assert "Coffee Delux" in req.data.decode("utf-8")
        assert "Roasted by us" in req.data.decode("utf-8")
        assert "Monthly delievey" in req.data.decode("utf-8")
        assert "Highest Quality" in req.data.decode("utf-8")
        assert 'name="sell_price-0"  value="5.0"  id="sell_price-0"' in req.data.decode(
            "utf-8"
        )


def test_admin_can_add_choice_group(
    session, app, client, admin_session, with_default_country_code_and_default_currency
):
    user = User.query.filter_by(email="admin@example.com").first()
    with user_set(app, user):
        req = client.post(
            "/admin/add-choice-group",
            follow_redirects=True,
            data={
                "title": "Colour choice",
            },
        )
        assert "Colour choice" in req.data.decode("utf-8")


def test_admin_can_add_an_option_to_a_choice_group(
    session, app, client, admin_session, with_default_country_code_and_default_currency
):
    user = User.query.filter_by(email="admin@example.com").first()
    with user_set(app, user):
        # First add a choice group (will have an id of 1)
        req = client.post(
            "/admin/add-choice-group",
            follow_redirects=True,
            data={
                "title": "Colour choice",
            },
        )

        # Now add an option to this new choice group
        req = client.post(
            "/admin/add-option/choice_group_id/1",
            follow_redirects=True,
            data={
                "title": "Light Blue",
            },
        )

        assert "Light Blue" in req.data.decode("utf-8")


@pytest.fixture(scope="function")
def admin_session(client, with_shop_owner):
    with client.session_transaction() as sess:
        sess["user_id"] = "admin@example.com"


def test_homepage(session, client, with_default_country_code_and_default_currency):
    req = client.get("/")
    assert req.status_code == 200


def test_magic_login_submission_as_shop_owner(
    session, client, with_shop_owner, with_default_country_code_and_default_currency
):
    """This does not test a successful login. Only that the login form submission
     is working.

     As a shop owner, when I submit an email address to the login form,
    the form submission succeeds.
    """
    req = client.post("/auth/login", data=dict(email="admin@example.com"))
    assert b"We've just sent you a login link." in req.data


def test_shop_owner_forgot_password_submission(
    session, client, with_shop_owner, with_default_country_code_and_default_currency
):
    """Test if forgot password form submission works for shop owner"""
    req = client.post(
        "/auth/forgot-password",
        follow_redirects=True,
        data=dict(email="admin@example.com"),
    )
    assert b"We&#39;ve sent you an email with a password reset link" in req.data


def test_apiv1_pages(session, client, with_default_country_code_and_default_currency):
    req = client.get("/api/v1/pages")
    assert req.status_code == 200
    assert req.json == []


def test_user_model(session):
    user = User()
    user.email = "test@example.com"
    session.add(user)
    session.commit()
    assert user.id > 0


def test_create_PriceList_and_price_list_rule_percent_discount(
    session,
    app,
    client,
    admin_session,
    with_shop_owner,
    with_default_country_code_and_default_currency,
):
    from subscribie.models import PriceList, PriceListRule, Plan
    from subscribie.database import database

    currency = "USD"
    priceList = PriceList(name="Christmas USD", currency=currency)
    # Prepare rule
    percent_discount = 25

    rule = PriceListRule(
        percent_discount=percent_discount, name=f"{percent_discount}% Discount"
    )
    priceList.rules.append(rule)
    database.session.add(priceList)
    database.session.commit()
    print(PriceList.query.all()[0].__dict__)
    price_list = PriceList.query.first()

    # Create a plan
    title = "Coffee Delux"
    interval_amount = 6.95
    sell_price = 10000
    user = User.query.filter_by(email="admin@example.com").first()
    with user_set(app, user):
        req = client.post(
            "/admin/add",
            follow_redirects=True,
            data={
                "company_name": "Coffee Castle",
                "slogan": "None",
                "email": "admin@example.com",
                "title-0": title,
                "selling_points-0-0": "Roasted by us",
                "selling_points-0-1": "Monthly delievey",
                "selling_points-0-3": "Highest Quality",
                "description-0": "A long description",
                "image-0": "",
                "subscription-0": "yes",
                "interval_amount-0": interval_amount,
                "interval_unit-0": "monthly",
                "days_before_first_charge-0": "0",
                "trial_period_days-0": "0",
                "instant_payment-0": "yes",
                "sell_price-0": sell_price,
                "note_to_buyer_message-0": "",
                "position-0": "",
            },
        )
        assert "Plan added." in req.data.decode("utf-8")

    plan = Plan.query.first()
    plan.price_lists.append(price_list)
    database.session.add(plan)
    database.session.commit()
    print(f"Ensure price rule is applied {percent_discount}% Discount")
    expected_sell_price = 750000
    expected_inverval_amount = 522
    assert plan.getPrice("USD")[0] == expected_sell_price
    assert plan.getPrice("USD")[1] == expected_inverval_amount
