import importlib
import sys
import time

import serial
from _helpers.logger import Logger


class BumpBarProcessor:
    def __init__(self, logger_instance: Logger, parameters: dict, commands: dict):
        self.parameters = parameters
        self.logger = logger_instance
        self.commands = commands

        self._communicate()

    def _communicate(self):
        self.logger.info("Attempting to open serial communication...")
        for k, v in self.parameters.items():
            self.logger.debug(f"  {k}: {v}")

        try:
            s = serial.Serial(
                self.parameters.get("port"),
                self.parameters.get("baud"),
                timeout=1
            )
            s.setDTR(True)
            s.setRTS(False)
            while s.is_open:
                if s.in_waiting > 0:
                    try:
                        rx_line = s.read()
                        self._responder(rx_line)
                        
                        if self.parameters.get("repeat_presses", False):
                            s.setDTR(False)
                            time.sleep(0.008)
                            s.setDTR(True)
                    except Exception as e:
                        print(e)

        except serial.SerialException as e:
            self.logger.error("Failed to open serial communication!")
            self.logger.debug(e)
        except OSError as e:
            self.logger.error("A communication error has occured, check your connection")
            self.logger.debug(e)
        except KeyboardInterrupt:
            sys.exit(0)
        finally:
            self.logger.info("Closing serial communication...")
            if 's' in locals():
                s.close()

    def _responder(self, rx_line):
        rx_hex = rx_line.hex().lower()
        self.logger.debug(f"Button pressed: {rx_hex}")
        if self.commands is not None:
            self._exec_action(rx_hex)

    def _exec_action(self, rx_hex):
        if not (action := self.commands.get(rx_hex)):
            self.logger.warning(f"No action configured for {rx_hex}")
            return

        try:
            if (plugin := action.get("plugin")) is not None:
                module = importlib.import_module(plugin)
                if hasattr(module, "run"):
                    module.run(self.logger, **action.get("kwargs", {}))
                else:
                    self.logger.error(f"'run' function not found in plugin: {plugin}")
            else:
                raise KeyError(f"No plugin was defined for action for: {rx_hex}")
        except Exception as e:
            self.logger.error(f"Failed to execute plugin for: {rx_hex}")
            self.logger.debug(str(e))
