import logging
from logging.handlers import QueueHandler, QueueListener
from TelegramHTTPHandler import TelegramHTTPHandler
import os
import sys
import queue
from dotenv import load_dotenv

load_dotenv(verbose=True)

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")
TELEGRAM_PYTHON_LOG_LEVEL = os.getenv("TELEGRAM_PYTHON_LOG_LEVEL", "WARNING")

logger = logging.getLogger()

handler = logging.StreamHandler()  # sys.stderr will be used by default

formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s %(funcName)s %(pathname)s:%(lineno)d"  # noqa
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
# See https://docs.python.org/3/howto/logging-cookbook.html#dealing-with-handlers-that-block # noqa
que = queue.Queue(-1)  # no limit on size
queue_handler = QueueHandler(que)

telegram_token = os.getenv("TELEGRAM_TOKEN", None)
telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", None)
telegramHandlerHost = "api.telegram.org"

telegramHandlerUrl = f"bot{telegram_token}/sendMessage?chat_id={telegram_chat_id}&text="

telegramHandler = TelegramHTTPHandler(
    telegramHandlerHost, url=telegramHandlerUrl, secure=True
)
logger.info(f"Setting TELEGRAM_PYTHON_LOG_LEVEL to {TELEGRAM_PYTHON_LOG_LEVEL}")
telegramHandler.setLevel(TELEGRAM_PYTHON_LOG_LEVEL)
listener = QueueListener(que, telegramHandler, respect_handler_level=True)
logger.addHandler(queue_handler)
listener.start()
