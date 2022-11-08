---
title: "Events & Signals"
date: 2022-11-05
weight: 2
description: >
  Subscribie emits **Signals** when an **Event** occurs, such as `signal_payment_failed`. This is achieved using the python [blinker library](https://blinker.readthedocs.io/en/stable/).
---


# How Signals & Events work together

For a more in depth generic explanation of signals see the [ official blinker documentation](https://blinker.readthedocs.io/en/stable/).


# Subscribie Signals

The following events are defined:

- `signal_journey_complete`
- `signal_payment_failed`

> By convention, signal names are prefixed with `signal_`


# How do I create an event? (aka How do I create a signal?)

> It's helpful to think in terms of **Signals** which emit notifications to all connected recievers. Many **Receivers** may be interested in a single event. For example, a new order your email notification system might be interested, plus your postal service. One **Signal** can have multiple **Receivers** connected to it.

First, you must have created a signal.
