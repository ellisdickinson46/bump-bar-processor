import platform
import subprocess

from _helpers.logger import Logger

class Plugin_PlatformCommand():
    def __init__(self, logger_instance: Logger, command):
        self.logger = logger_instance
        self.command = command
        self.system = platform.system()

        self._execute_command(self.command)

    def _execute_command(self, command):
        self.logger.info(f"Executing on {self.system}: {command}")
        try:
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            self.logger.info(f"Result: {result.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Command failed: {e}")


def run(logger, **kwargs):
    Plugin_PlatformCommand(logger, **kwargs)
