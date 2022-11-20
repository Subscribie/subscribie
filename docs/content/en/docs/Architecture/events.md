---
title: "Events & Signals"
date: 2022-11-05
weight: 2
description: >
  Subscribie emits **Signals** when an **Event** occurs, such as `signal_payment_failed`. This is achieved using the python [blinker library](https://blinker.readthedocs.io/en/stable/).
---


# How Signals & Events work together

When an 'event' happens, you find out by receiving a signal- but you must *subscribie* to the signals you're interested in.

For a more in depth generic explanation of signals see the [ official blinker documentation](https://blinker.readthedocs.io/en/stable/).


# Subscribie Signals

> By convention, signal names are prefixed with `signal_`

For example:

- `signal_journey_complete`
- `signal_payment_failed`

Structure:

- `signals.py` is where signals are defined
- `receivers.py` is where signals are connected to recievers
- `notifications.py` &amp; `email.py`


# How do I create an event?

> It's helpful to think in terms of **Signals** which emit notifications to all connected recievers. Many **Receivers** may be interested in a single event. For example, a new order your email notification system might be interested, plus your postal service. One **Signal** can have multiple **Receivers** connected to it.

First, you must have created a signal.

# How are events (signals) fired?

Events are 'fired' when `send` is called on the signal.
For example, `send()` is called on the `journey_complete` signal when
a subscriber gets to the 'thank you' page. Any recievers connected to that
signal withh receive that event.

> Note in the example below, we are passing the current app, and the associated email
  address for the event. Be careful doing this if your reciever runs in a background thread,
  as that will not have access to the application context.

```
journey_complete.send(current_app._get_current_object(), email=email)
```
