---
title: "Logging"
date: 2022-11-05
weight: 2
description: >
  How to view Subscribie logs during development / testing / production.
---


# Logging

Subscribie using python standard `logging` module, with log handlers configred for stdout and Telegram.

> tldr: Set `PYTHON_LOG_LEVEL=DEBUG` in your `.env` settings file.

# Viewing logs &amp; Changing the Log level

In the file `.env`, set the `PYTHON_LOG_LEVEL` to `DEBUG` or lower.

```
PYTHON_LOG_LEVEL=DEBUG
```

Then re-start Subscribie.

Loglevel options are:

- `DEBUG`
- `INFO`
- `WARNING`
- `ERROR`
- `CRITICAL`

See also: [When to use logging](https://docs.python.org/3/howto/logging.html#when-to-use-logging)

## Telegram logging

In the same way, you can configure telegram log level verbosity by setting `TELEGRAM_PYTHON_LOG_LEVEL`
in your `.env` settings file.

```
TELEGRAM_PYTHON_LOG_LEVEL=ERROR
```

# Logging code

Where is the logger setup?

See [`logger.py`](https://github.com/Subscribie/subscribie/blob/master/subscribie/logger.py)

# Common Python logging mistakes

### I see no logs, even though I'm doing `log.warning` etc

If your log `PYTHON_LOG_LEVEL` is too high, e.g. if set to `ERROR`, then the logger (or more precisely, a given log handler, won't display any log messages lower than `ERROR`.

### Thinking there is only "one" python logger

Python logging has two key concepts: The **logger**, and log **handlers**.
In Subscribie, we log to stdout using the built-in [`StreamHandler`](https://docs.python.org/3/library/logging.handlers.html#streamhandler) and use an *additonal* built-in handler [`QueueHandler`](https://docs.python.org/3/library/logging.handlers.html#queuehandler) which is configured to send to Telegram if configured.

See [`logger.py`](https://github.com/Subscribie/subscribie/blob/master/subscribie/logger.py) for implementation.


## See also

[How to send telegram messages with python tutorial](https://blog.karmacomputing.co.uk/how-to-send-telegram-messages-with-python-tutorial/)
