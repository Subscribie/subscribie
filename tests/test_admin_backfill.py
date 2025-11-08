"""
Test admin backfill interface

Tests the user-friendly backfill data form at /admin/backfill
introduced in issue #1476.
"""
import pytest
from subscribie.models import User
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from flask import appcontext_pushed, g


@contextmanager
def user_set(app, user):
    """Context manager to set g.user for testing authenticated routes"""
    def handler(sender, **kwargs):
        g.user = user

    with appcontext_pushed.connected_to(handler, app):
        yield


@pytest.fixture
def admin_session(client, with_shop_owner):
    """Create an authenticated admin session"""
    with client.session_transaction() as sess:
        sess["user_id"] = "admin@example.com"


class TestAdminBackfillInterface:
    """Test the admin backfill data interface"""

    def test_backfill_form_renders_successfully(
        self,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test that GET /admin/backfill renders the form"""
        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.get("/admin/backfill")

            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Check form elements are present
            assert "Synchronise Data from Stripe" in response_data
            assert "Number of days to backfill:" in response_data
            assert 'name="days"' in response_data
            assert 'value="30"' in response_data  # Default value

            # Check all data type checkboxes are present and checked by default
            assert 'name="backfill_types" value="transactions"' in response_data
            assert 'name="backfill_types" value="subscriptions"' in response_data
            assert 'name="backfill_types" value="persons"' in response_data
            assert 'name="backfill_types" value="invoices"' in response_data
            assert 'id="backfill_transactions"' in response_data
            assert 'id="backfill_subscriptions"' in response_data
            assert 'id="backfill_persons"' in response_data
            assert 'id="backfill_invoices"' in response_data
            assert 'checked' in response_data  # At least some checkboxes are checked

    @patch("subscribie.blueprints.admin.backfill_transactions")
    @patch("subscribie.blueprints.admin.backfill_subscriptions")
    @patch("subscribie.blueprints.admin.backfill_persons")
    @patch("subscribie.blueprints.admin.backfill_stripe_invoices")
    def test_backfill_form_submission_with_all_types(
        self,
        mock_invoices,
        mock_persons,
        mock_subscriptions,
        mock_transactions,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test POST /admin/backfill with all data types selected

        Note: This test verifies the background task is triggered but does NOT
        wait for it to complete. The backfill functions run in a separate thread.
        To verify they actually execute, check the application logs when running
        the app manually.
        """
        import time

        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.post(
                "/admin/backfill",
                data={
                    "days": "30",
                    "backfill_types": ["transactions", "subscriptions", "persons", "invoices"],
                },
                follow_redirects=True,
            )

            # Should redirect back to form
            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Should show the backfill form again after redirect
            assert "Backfill Data from Stripe" in response_data or "Synchronise Data from Stripe" in response_data

            # Give background thread a moment to start
            time.sleep(0.5)

            # Verify the backfill functions were called (they run in background thread)
            # Note: These may not be called yet if thread hasn't started
            mock_transactions.assert_called_with(30)
            mock_subscriptions.assert_called_with(30)
            mock_persons.assert_called_with(30)
            mock_invoices.assert_called_with(30)

    @patch("subscribie.blueprints.admin.backfill_transactions")
    def test_backfill_form_submission_with_single_type(
        self,
        mock_transactions,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test POST /admin/backfill with only transactions selected"""
        import time

        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.post(
                "/admin/backfill",
                data={
                    "days": "7",
                    "backfill_types": ["transactions"],
                },
                follow_redirects=True,
            )

            # Should redirect back to form
            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Should show the backfill form again after redirect
            assert "Backfill Data from Stripe" in response_data or "Synchronise Data from Stripe" in response_data

            # Give background thread a moment to start
            time.sleep(0.5)

            # Verify the backfill function was called
            mock_transactions.assert_called_with(7)

    def test_backfill_form_submission_with_no_types_selected(
        self,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test POST /admin/backfill with no data types selected shows error"""
        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.post(
                "/admin/backfill",
                data={
                    "days": "30",
                    # No backfill_types provided
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Check error message
            assert "Please select at least one data type to backfill" in response_data

    def test_backfill_form_submission_with_invalid_days_too_low(
        self,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test POST /admin/backfill with days < 1 shows error"""
        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.post(
                "/admin/backfill",
                data={
                    "days": "0",
                    "backfill_types": ["transactions"],
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Check error message
            assert "Please enter a number between 1 and 365 days" in response_data

    def test_backfill_form_submission_with_invalid_days_too_high(
        self,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test POST /admin/backfill with days > 365 shows error"""
        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.post(
                "/admin/backfill",
                data={
                    "days": "400",
                    "backfill_types": ["transactions"],
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Check error message
            assert "Please enter a number between 1 and 365 days" in response_data

    def test_backfill_form_submission_with_invalid_days_not_a_number(
        self,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test POST /admin/backfill with non-numeric days shows error"""
        user = User.query.filter_by(email="admin@example.com").first()
        with user_set(app, user):
            response = client.post(
                "/admin/backfill",
                data={
                    "days": "invalid",
                    "backfill_types": ["transactions"],
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            response_data = response.data.decode("utf-8")

            # Check error message
            assert "Invalid number of days provided" in response_data

    def test_backfill_requires_authentication(
        self,
        db_session,
        app,
        client,
        with_default_country_code_and_default_currency,
    ):
        """Test that /admin/backfill requires authentication"""
        # Don't use admin_session fixture - test without authentication
        response = client.get("/admin/backfill", follow_redirects=False)

        # Should redirect to login
        assert response.status_code == 302
        assert "/auth/login" in response.location or "login" in response.location.lower()

    @patch("subscribie.blueprints.admin.backfill_transactions")
    def test_legacy_api_endpoint_preserved(
        self,
        mock_backfill_transactions,
        db_session,
        app,
        client,
        admin_session,
        with_default_country_code_and_default_currency,
    ):
        """Test that legacy API endpoint /admin/backfill/transactions/<days> still works"""
        user = User.query.filter_by(email="admin@example.com").first()

        with user_set(app, user):
            # Test JSON API response (default behavior)
            response = client.get(
                "/admin/backfill/transactions/30",
                follow_redirects=False,
            )

            # Should return JSON response for API calls
            assert response.status_code == 200
            response_data = response.data.decode("utf-8")
            assert "backfill_transactions for 30 days completed" in response_data

            # Verify backfill function was called
            mock_backfill_transactions.assert_called_once_with(30)
