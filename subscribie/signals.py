# -*- coding: utf-8 -*-
"""
    subscribie.signals
    ~~~~~~~~~~~~~

    Implements signals using blinker.

    See also subscribie.receivers
      which lists receivers which connect to the signals
      this allows multiple receivers to listen to one signal.

      For example, multiple receivers may listen for the
      payment_failed signal.
"""
from blinker import signal

# Subscribie Core signals.  For usage examples grep the source code
journey_complete = signal("journey-complete")

signal_payment_failed = signal("payment-failed")
