from _helpers.logger import Logger

class Plugin_HelloWorld():
    def __init__(self, logger_instance: Logger):
        self.logger = logger_instance

        self.logger.debug("Hello from plugin")


def run(logger):
    Plugin_HelloWorld(logger)
