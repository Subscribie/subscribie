from logging.handlers import HTTPHandler
import requests


class TelegramHTTPHandler(HTTPHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def emit(self, record):
        """
        Emit log record to Telegram
        """
        try:
            host = self.host
            if self.secure:
                scheme = "https://"
            else:
                scheme = "http://"
            url = self.url
            data = str(self.mapLogRecord(record))[
                0:4000
            ]  # Truncate to max Telegram message size
            url = f"{url}{data}"
            requests.get(scheme + host + "/" + url)
        except Exception:
            self.handleError(record)
