"""Regression tests for issue #1441.

The bug: when Stripe sends a ``payment_intent.payment_failed`` webhook for a
charge whose ``billing_details.name`` is ``None``, the notifier used to crash
with ``'NoneType' object has no attribute 'split'`` and the subscriber never
received the "your payment failed" email at all.

These tests exercise the notifier directly with the boundary inputs Stripe can
produce in the wild.
"""
import logging
from unittest.mock import patch

from subscribie.notifications import subscriberPaymentFailedNotification


def test_none_subscriber_name_does_not_raise(
    db_session,
    app,
    with_default_country_code_and_default_currency,
):
    """Before the fix this raised AttributeError on ``None.split(' ')``."""
    with patch("subscribie.notifications.EmailMessageQueue") as mq:
        subscriberPaymentFailedNotification(
            subscriber_email="customer@example.com",
            subscriber_name=None,
            failure_message="Your card was declined.",
            failure_code="card_declined",
            app=app,
        )
        assert mq.return_value.queue.called, (
            "Email should still be queued when subscriber_name is None; "
            "a missing first name must not block the failure notification."
        )


def test_none_subscriber_email_is_logged_and_skipped(
    db_session,
    app,
    with_default_country_code_and_default_currency,
    caplog,
):
    """Without an email address there is nowhere to send the notification.
    We must log an error rather than crash, and must not attempt to queue
    an email to ``None``."""
    with patch("subscribie.notifications.EmailMessageQueue") as mq, \
            caplog.at_level(logging.ERROR, logger="subscribie.notifications"):
        subscriberPaymentFailedNotification(
            subscriber_email=None,
            subscriber_name=None,
            failure_message="Your card was declined.",
            failure_code="card_declined",
            app=app,
        )
        assert not mq.return_value.queue.called
        assert any(
            "subscriber_email is missing" in r.message for r in caplog.records
        )


def test_happy_path_still_queues_email(
    db_session,
    app,
    with_default_country_code_and_default_currency,
):
    with patch("subscribie.notifications.EmailMessageQueue") as mq:
        subscriberPaymentFailedNotification(
            subscriber_email="customer@example.com",
            subscriber_name="Ada Lovelace",
            failure_message="Your card was declined.",
            failure_code="card_declined",
            app=app,
        )
        assert mq.return_value.queue.called
