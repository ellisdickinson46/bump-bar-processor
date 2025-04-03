import requests

from _helpers.logger import Logger

class Plugin_WebRequest():
    def __init__(self, logger_instance: Logger, **kwargs):
        self.logger = logger_instance
        self.method = kwargs.pop("method").upper()
        self.url = kwargs.pop("url")
        self.json = kwargs.pop("json", None)

        valid_methods = [
            "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
        ]
        if self.method in valid_methods:
            self._execute_command()

    def _execute_command(self):
        self.logger.info(f"Sending {self.method} request")
        self.logger.debug(f"  url: {self.url}")
        self.logger.debug(f"  json: {self.json}")
        x = requests.request(
            self.method,
            self.url,
            json=self.json,
            timeout=2
        )
        self.logger.info(f"Response: {x}")


def run(logger, **kwargs):
    Plugin_WebRequest(logger, **kwargs)
