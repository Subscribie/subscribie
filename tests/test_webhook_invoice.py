import json
from unittest.mock import patch
import pytest


def test_invoice_created_injects_fee(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that the invoice.created webhook correctly calculates
    and injects the 2.5% + 40p application_fee_amount onto draft recurring invoices.
    """
    # 10.00 GBP represented in pence
    invoice_total = 1000

    # Expected fee: (1000 * 0.025) + 40 = 25 + 40 = 65
    expected_fee = 65

    # Mock payload from Stripe
    payload = {
        "livemode": False,
        "type": "invoice.created",
        "account": "acct_1TestConnectAccount",
        "data": {
            "object": {
                "id": "in_1TestInvoice",
                "status": "draft",
                "subscription": "sub_1TestSubscription",
                "total": invoice_total,
            }
        },
    }

    with patch(
        "subscribie.blueprints.checkout.stripe.Invoice.modify"
    ) as mock_invoice_modify:
        with patch(
            "subscribie.blueprints.checkout.get_stripe_secret_key",
            return_value="sk_test_123",
        ):
            with patch(
                "subscribie.blueprints.checkout.get_stripe_connect_account_id",
                return_value="acct_1TestConnectAccount",
            ):
                response = client.post(
                    "/stripe_webhook",
                    data=json.dumps(payload),
                    content_type="application/json",
                )

            # Assert webhook processed successfully
            assert response.status_code == 200

            # Assert stripe.Invoice.modify was called exactly once
            mock_invoice_modify.assert_called_once_with(
                "in_1TestInvoice",
                application_fee_amount=expected_fee,
                stripe_account="acct_1TestConnectAccount",
            )


def test_invoice_created_caps_fee_at_total(
    client, app, db_session, with_default_country_code_and_default_currency
):
    """
    Test that the application fee cannot exceed the total invoice amount.
    """
    # 30p total invoice
    invoice_total = 30

    # Expected fee raw: (30 * 0.025) + 40 = 0.75 + 40 = 40.75 (int -> 40)
    # But fee cannot exceed total, so 30
    expected_fee = 30

    payload = {
        "type": "invoice.created",
        "livemode": False,
        "account": "acct_1TestConnectAccount",
        "data": {
            "object": {
                "id": "in_1TestInvoice",
                "status": "draft",
                "subscription": "sub_1TestSubscription",
                "total": invoice_total,
            }
        },
    }

    with patch(
        "subscribie.blueprints.checkout.stripe.Invoice.modify"
    ) as mock_invoice_modify:
        with patch(
            "subscribie.blueprints.checkout.get_stripe_secret_key",
            return_value="sk_test_123",
        ):
            with patch(
                "subscribie.blueprints.checkout.get_stripe_connect_account_id",
                return_value="acct_1TestConnectAccount",
            ):
                response = client.post(
                    "/stripe_webhook",
                    data=json.dumps(payload),
                    content_type="application/json",
                )

            assert response.status_code == 200
            mock_invoice_modify.assert_called_once_with(
                "in_1TestInvoice",
                application_fee_amount=expected_fee,
                stripe_account="acct_1TestConnectAccount",
            )
