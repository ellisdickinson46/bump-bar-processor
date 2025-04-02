import sys
import time

import serial
from _helpers.logger import Logger


class BumpBarProcessor:
    def __init__(self, logger_instance: Logger, parameters: dict):
        self.parameters = parameters
        self.logger = logger_instance
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
        rx_hex = rx_line.hex().upper()
        self.logger.debug(f"Button pressed: {rx_hex}")
