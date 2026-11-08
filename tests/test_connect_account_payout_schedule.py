from unittest.mock import patch, MagicMock
from flask import g
from subscribie.utils import create_stripe_connect_account


def test_create_stripe_connect_account_configures_weekly_payouts(app):
    """
    Test that create_stripe_connect_account sets payout schedule to weekly (friday)
    to reduce per-payout fees and maintain a balance float against refunds.
    """
    company = MagicMock()
    company.name = "Test Subscription Company"

    with app.test_request_context("http://example.com/"):
        g.user = MagicMock()
        g.user.email = "shopowner@example.com"

        with patch(
            "subscribie.utils.get_stripe_secret_key", return_value="sk_test_123"
        ):
            with patch("subscribie.utils.stripe.Account.create") as mock_account_create:
                mock_account_create.return_value = MagicMock(id="acct_1WeeklyTest")

                account = create_stripe_connect_account(
                    company=company,
                    country_code="GB",
                    default_currency="GBP",
                )

                assert account.id == "acct_1WeeklyTest"
                assert mock_account_create.called
                call_kwargs = mock_account_create.call_args[1]

                assert "settings" in call_kwargs
                payout_settings = call_kwargs["settings"]["payouts"]["schedule"]
                assert payout_settings["interval"] == "weekly"
                assert payout_settings["weekly_anchor"] == "friday"
