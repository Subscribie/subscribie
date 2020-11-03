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


def test_admin_can_view_dashboard(session, app, client, admin_session):
    user = User.query.filter_by(email="admin@example.com").first()
    with user_set(app, user):
        client.get("/admin/dashboard", follow_redirects=True)


def test_admin_cal_add_plan(session, app, client, admin_session):
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
                "image-0": "",
                "subscription-0": "yes",
                "interval_amount-0": "6.95",
                "interval_unit-0": "monthly",
                "days_before_first_charge-0": "0",
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
        assert (
            '<input name="interval_amount-0" id="interval_amount-0"\n                        \n                        value="6.95"'  # noqa
            in req.data.decode("utf-8")
        )
        assert 'name="sell_price-0" value="5.0"' in req.data.decode("utf-8")


@pytest.fixture(scope="function")
def admin_session(client, with_shop_owner):
    user = User.query.filter_by(email="admin@example.com").first()
    with client.session_transaction() as sess:
        sess["user_id"] = user.email


def test_homepage(session, client):
    req = client.get("/")
    assert req.status_code == 200


def test_magic_login_submission_as_shop_owner(session, client, with_shop_owner):
    """This does not test a successful login. Only that the login form submission
     is working.

     As a shop owner, when I submit an email address to the login form,
    the form submission succeeds.
    """
    req = client.post("/auth/login", data=dict(email="admin@example.com"))
    assert b"We've just sent you a login link." in req.data


def test_shop_owner_forgot_password_submission(session, client, with_shop_owner):
    """Test if forgot password form submission works for shop owner"""
    req = client.post(
        "/auth/forgot-password",
        follow_redirects=True,
        data=dict(email="admin@example.com"),
    )
    assert (
        b"We&#39;ve sent you an email with a password reset link, please check your spam/junk folder too"  # noqa
        in req.data
    )


def test_user_model(session):
    user = User()
    user.email = "test@example.com"
    session.add(user)
    session.commit()
    assert user.id > 0
