"""Regression tests for issue #1441.

Issue: https://github.com/Subscribie/subscribie/issues/1441

The bug: when Stripe sends a ``payment_intent.payment_failed`` webhook for a
charge whose ``billing_details.name`` is ``None``, the notifier used to crash
in ``subscribie/notifications.py`` with
``'NoneType' object has no attribute 'split'`` and the subscriber never
received the "your payment failed" email at all.

These tests exercise the notifier directly with the boundary inputs Stripe can
produce in the wild.
"""
import logging
from unittest.mock import MagicMock, patch

from subscribie.notifications import subscriberPaymentFailedNotification


def _call_with_mocks(app, **kwargs):
    """Call the notifier with every external dependency mocked. Returns the
    EmailMessageQueue mock so the test can assert queue() was invoked."""
    company = MagicMock()
    company.name = "Acme"
    setting = MagicMock()
    setting.reply_to_email_address = None
    user = MagicMock()
    user.email = "admin@example.com"
    with patch("subscribie.notifications.EmailMessageQueue") as mq, \
            patch("subscribie.notifications.Company") as company_cls, \
            patch("subscribie.notifications.Setting") as setting_cls, \
            patch("subscribie.notifications.User") as user_cls:
        company_cls.query.first.return_value = company
        setting_cls.query.first.return_value = setting
        user_cls.query.first.return_value = user
        subscriberPaymentFailedNotification(app=app, **kwargs)
        return mq


def test_none_subscriber_name_does_not_raise(app):
    """Before the fix this raised AttributeError on ``None.split(' ')``."""
    mq = _call_with_mocks(
        app,
        subscriber_email="customer@example.com",
        subscriber_name=None,
        failure_message="Your card was declined.",
        failure_code="card_declined",
    )
    assert mq.return_value.queue.called, (
        "Email should still be queued when subscriber_name is None; "
        "a missing first name must not block the failure notification."
    )


def test_none_subscriber_email_is_logged_and_skipped(app, caplog):
    """Without an email address there is nowhere to send the notification.
    We must log an error rather than crash, and must not attempt to queue
    an email to ``None``."""
    with caplog.at_level(logging.ERROR, logger="subscribie.notifications"):
        mq = _call_with_mocks(
            app,
            subscriber_email=None,
            subscriber_name=None,
            failure_message="Your card was declined.",
            failure_code="card_declined",
        )
    assert not mq.return_value.queue.called
    assert any(
        "subscriber_email is missing" in r.message for r in caplog.records
    )


def test_happy_path_still_queues_email(app):
    mq = _call_with_mocks(
        app,
        subscriber_email="customer@example.com",
        subscriber_name="Ada Lovelace",
        failure_message="Your card was declined.",
        failure_code="card_declined",
    )
    assert mq.return_value.queue.called
