# -*- coding: utf-8 -*-
"""
    hedgehog.signals
    ~~~~~~~~~~~~~

    Implements signals based on blinker if available, otherwise
    falls silently back to a noop.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from blinker import signal

# Hedgehog Core signals.  For usage examples grep the source code
#journey_complete = signal('journey-complete')

