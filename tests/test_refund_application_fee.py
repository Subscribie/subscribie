import pytest
from unittest.mock import patch
from contextlib import contextmanager
from flask import appcontext_pushed, g
from subscribie.models import User, Transaction, database


@contextmanager
def user_set(app, user):
    def handler(sender, **kwargs):
        g.user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def admin_session(client, with_shop_owner):
    with client.session_transaction() as sess:
        sess["user_id"] = "admin@example.com"


def test_refund_stripe_subscription_passes_refund_application_fee(
    client, app, db_session, admin_session, with_default_country_code_and_default_currency
):
    """
    Test that refunding a subscription charge sets refund_application_fee=True
    to avoid merchant negative balances.
    """
    user = User.query.filter_by(email="admin@example.com").first()

    # Create a test transaction
    tx = Transaction(
        external_id="pi_test_refund_123",
        amount=2000,
        currency="gbp",
    )
    database.session.add(tx)
    database.session.commit()

    with user_set(app, user):
        with patch("subscribie.blueprints.admin.stripe.Refund.create") as mock_refund_create:
            with patch(
                "subscribie.blueprints.admin.get_stripe_connect_account_id",
                return_value="acct_1TestConnectAccount",
            ):
                mock_refund_create.return_value.id = "re_test_123"

                response = client.get(
                    "/admin/stripe/subscriptions/pi_test_refund_123/actions/refund/?confirm=1",
                    follow_redirects=False,
                )

                assert response.status_code == 302
                mock_refund_create.assert_called_once_with(
                    payment_intent="pi_test_refund_123",
                    refund_application_fee=True,
                    stripe_account="acct_1TestConnectAccount",
                )
                assert tx.external_refund_id == "re_test_123"
