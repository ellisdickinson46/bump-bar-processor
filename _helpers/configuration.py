from argparse import Namespace
import glob
import sys

import serial
from _helpers.logger import Logger
from _helpers.data import JSONHandler


class CommandParser:
    def __init__(self, logger_instance: Logger, parameters: Namespace):
        self.logger = logger_instance
        self.parameters = parameters
        self.cmd_result = {}

        commands = {
            "hw-test": self._config_from_args,
            "run": self._config_from_file,
            "list-ports": self.list_ports
        }
        try:
            if (cmd_result := commands[self.parameters.command]()) is not None:
                self.cmd_result = cmd_result
        except KeyError as e:
            self.logger.error('Command not found', e)

    def _config_from_args(self):
        self.logger.info("Launching with configuration from command line...")
        return {
            "type": "launch",
            "parameters": {
                "baud": self.parameters.baud,
                "port": self.parameters.port,
                "auto_reconnect": self.parameters.a,
                "repeat_presses": self.parameters.r
            },
            "commands": None
        }

    def _config_from_file(self):
        self.logger.info("Launching with configuration from a configuration file...")
        try:
            config = JSONHandler(self.parameters.config_file)
        except Exception as e:
            self.logger.error(e)
            return

        return {
            "type": "launch",
            "parameters": {
                "baud": config.get("connection.baud"),
                "port": config.get("connection.port"),
                "auto_reconnect": config.get("feature_flags.enable_auto_reconnect"),
                "repeat_presses": config.get("feature_flags.enable_repeat_presses")
            },
            "commands": config.get("commands")
        }

    def list_ports(self):
        """ Finds all serial ports and returns a list containing them

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :raises OSError:
                If a serial port cannot be opened (handled internally)
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = [f"COM{(i + 1)}" for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # This excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        viable_ports = []
        for port_name in ports:
            try:
                port = serial.Serial(port_name)     # Try to open a port
                port.close()                        # Close the port if sucessful
                viable_ports.append(port_name)      # Add to list of good ports
            except OSError:                         # If unsuccessful
                pass
        return {
            "type": "output",
            "return": viable_ports
        }
