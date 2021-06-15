# -*- coding: utf-8 -*-
"""
    subscribie.signals
    ~~~~~~~~~~~~~

    Implements signals using blinker.

    See also subscribie.receivers
      which lists receivers which connect to the signals
"""
from blinker import signal

# Subscribie Core signals.  For usage examples grep the source code
journey_complete = signal("journey-complete")
