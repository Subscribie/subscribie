import logging
import os
import sys

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")

logger = (
    logging.getLogger()
)  # Will return root logger, don't set this to __name__ in this rool level logger, otherwise default formatting or handlers are not set # noqa

# https://docs.python.org/3/library/logging.handlers.html#logging.StreamHandler
handler = logging.StreamHandler()  # sys.stderr will be used by default

formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s %(funcName)s %(pathname)s:%(lineno)d"  # noqa
)

# https://docs.python.org/3/library/logging.html#logging.Handler
handler.setFormatter(formatter)
handler.setLevel(
    PYTHON_LOG_LEVEL
)  # Both loggers and handlers have a setLevel method  noqa
logger.addHandler(handler)

logger.setLevel(PYTHON_LOG_LEVEL)


# Log all uncuaght exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception
