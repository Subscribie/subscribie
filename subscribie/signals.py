# -*- coding: utf-8 -*-
"""
    subscribie.signals
    ~~~~~~~~~~~~~

    Implements signals using blinker.

    See also subscribie.receivers
      which lists receivers which connect to the signals
      this allows multiple receivers to listen to one signal.

      For example, multiple receivers may listen for the
      payment_failed signal, because multiple actors may be
      interested in that event (e.g. bother the Shop owner
      and a Subscriber wants to know, and a logging system etc)
"""
from blinker import signal
from subscribie.notifications import newSubscriberEmailNotification
from subscribie.receivers import (
    receiver_send_subscriber_payment_failed_notification_email,
    receiver_send_email,
    receiver_attach_documents_to_subscription,
)

# Subscribie Core signals.  For usage examples grep the source code
signal_journey_complete = signal("journey-complete")

signal_payment_failed = signal("payment-failed")

# Signal Subscriptions / Subscribing to Signals
"""
Signal.connect() registers a function to be invoked each time the signal is
emitted. Connected functions are always passed the object that caused the
signal to be emitted.

See https://blinker.readthedocs.io/en/stable/#subscribing-to-signals
"""


def register_signal_handlers():
    """Connect signals to recievers
    This is called during flask app startup in views.py
    """
    signal_journey_complete.connect(newSubscriberEmailNotification)
    signal_journey_complete.connect(receiver_send_email)
    signal_journey_complete.connect(receiver_attach_documents_to_subscription)
    signal_payment_failed.connect(
        receiver_send_subscriber_payment_failed_notification_email
    )
