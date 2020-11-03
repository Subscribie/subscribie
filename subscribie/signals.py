# -*- coding: utf-8 -*-
"""
    subscribie.signals
    ~~~~~~~~~~~~~

    Implements signals using blinker.

    Influenced by Flask framework signals (c) 2015 by Armin Ronacher.
"""
from blinker import signal

# Subscribie Core signals.  For usage examples grep the source code
journey_complete = signal("journey-complete")
