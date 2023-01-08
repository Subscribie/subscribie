import logging
import coloredlogs
from flask import has_request_context, request
from logging.handlers import QueueHandler, QueueListener
from subscribie.TelegramHTTPHandler import TelegramHTTPHandler
import os
import sys
import queue

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")
TELEGRAM_PYTHON_LOG_LEVEL = os.getenv("TELEGRAM_PYTHON_LOG_LEVEL", "ERROR")

logger = logging.getLogger()
handler = logging.StreamHandler()  # sys.stderr will be used by default


class RequestFormatter(coloredlogs.ColoredFormatter):
    def format(self, record):
        if has_request_context():
            record.url = request.url
            record.remote_addr = request.remote_addr
        else:
            record.url = None
            record.remote_addr = None

        return super().format(record)


formatter = RequestFormatter(
    "[%(asctime)s] %(remote_addr)s requested %(url)s %(name)-12s %(levelname)-8s %(message)s %(funcName)s %(pathname)s:%(lineno)d"  # noqa
)

handler.setFormatter(formatter)
handler.setLevel(PYTHON_LOG_LEVEL)  # Both loggers and handlers have a setLevel method
logger.addHandler(handler)
logger.setLevel(PYTHON_LOG_LEVEL)


# Log all uncuaght exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


# Telegram logging
if os.getenv("FLASK_ENV", None) != "development":
    # See https://docs.python.org/3/howto/logging-cookbook.html#dealing-with-handlers-that-block # noqa
    que = queue.Queue(-1)  # no limit on size
    queue_handler = QueueHandler(que)

    telegram_token = os.getenv("TELEGRAM_TOKEN", None)
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", None)
    telegramHandlerHost = "api.telegram.org"

    telegramHandlerUrl = (
        f"bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text="
    )

    telegramHandler = TelegramHTTPHandler(
        telegramHandlerHost, url=telegramHandlerUrl, secure=True
    )
    logger.info(f"Setting TELEGRAM_PYTHON_LOG_LEVEL to {TELEGRAM_PYTHON_LOG_LEVEL}")
    telegramHandler.setLevel(TELEGRAM_PYTHON_LOG_LEVEL)
    listener = QueueListener(que, telegramHandler, respect_handler_level=True)
    logger.addHandler(queue_handler)
    listener.start()
