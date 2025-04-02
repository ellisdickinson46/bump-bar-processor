from argparse import Namespace
import glob
import sys

import serial
from _helpers.logger import Logger


class CommandParser:
    def __init__(self, logger_instance: Logger, parameters: Namespace):
        self.logger = logger_instance
        self.parameters = parameters
        self.cmd_result = {}

        commands = {
            "run": self._config_from_args,
            "run-config": self._config_from_file,
            "list-ports": self.list_ports
        }
        try:
            self.cmd_result = commands[self.parameters.command]()
        except KeyError as e:
            self.logger.error('Command not found', e)

    def _config_from_args(self):
        self.logger.info("Launching configuration from command line...")
        return {
            "type": "launch",
            "parameters": {
                "baud": self.parameters.baud,
                "port": self.parameters.port,
                "auto_reconnect": self.parameters.a,
                "repeat_presses": self.parameters.r
            }
        }

    def _config_from_file(self):
        self.logger.info("Launching configuration from configuration file...")
        return {
            "type": "launch",
            "parameters": {
                "baud": self.parameters.baud,
                "port": self.parameters.port,
                "auto_reconnect": self.parameters.a,
                "repeat_presses": self.parameters.r
            }
        }

    def list_ports(self):
        """ Finds all serial ports and returns a list containing them

            :raises EnvironmentError:
                On unsupported or unknown platforms
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
            except OSError:              # If unsuccessful
                pass
        return {
            "type": "output",
            "return": viable_ports
        }
