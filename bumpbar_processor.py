"""
bumpbar_processor.py

Process serial inputs from a Panasonic JS140MS or TG3 Bump Bar (KBA-FP10A)
"""

__author__    = "Ellis Dickinson"
__copyright__ = "Copyright 2024, ByteFloater"

import argparse
import glob
import os
import sys
import time
import yaml

import serial
from logbook import Logger, StreamHandler


# Running variable default declarations
BAUD_RATE = None
PORT_NAME = None
REPEAT_PRESSES = False
AUTO_RECONNECT = True
GOOD_CONFIG = False


def list_ports():
    """ Finds all serial ports and returns a list containing them

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = [f"COM{(i + 1)}" for i in range(256)]
        print(ports)
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # This excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port_name in ports:
        try:
            port = serial.Serial(port_name)     # Try to open a port
            port.close()                        # Close the port if sucessful
            result.append(port_name)            # Add to list of good ports
        except (IOError, OSError):            # If unsuccessful
            pass
    return result

def execute_cmd(serial_conn, key_input):
    """Run defined commands"""
    if REPEAT_PRESSES:
        serial_conn.setDTR(False)

    try:
        command = config['button_commands'][f"button_{key_input}"]
        if command:
            os.system(command)
            log.info(f"Command for input '{key_input}' executed")
        else:
            log.debug(f"No command defined for {key_input}")
    except TypeError:
        log.error("Configuration invalid, please check your configuration file syntax is correct.")

    if REPEAT_PRESSES:
        time.sleep(0.01)
        serial_conn.setDTR(True)


parser = argparse.ArgumentParser()
parser.add_argument("-b", "--baud", default="1200", help="Baud Rate (defaults to 1200)")
parser.add_argument("-c", "--configuration", help="Configuration File")
parser.add_argument("-p", "--port", help="Serial Port Name/Path")
args = parser.parse_args()

StreamHandler(sys.stdout).push_application()
log = Logger('BumpBarProcessor')
log.info("Starting Bump Bar Processor")


# Load the configuration YAML file, if specified
if args.configuration:
    try:
        with open(args.configuration, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            log.info("Configuration file found!")

            BAUD_RATE = config['connection']['baud']
            PORT_NAME = config['connection']['port_name']
            REPEAT_PRESSES = config['repeat_presses']
            AUTO_RECONNECT = config['auto_reconnect']
            MAX_RECONNECTS = config['max_reconnects']

            GOOD_CONFIG = True
            log.debug("Configuration values set successfully")

    except FileNotFoundError:
        log.error('Configuration file not found at the path specified, using in-line arguments.')
    except TypeError:
        log.error("Configuration invalid, please check your configuration file syntax is correct.")
    except KeyError as error:
        log.error(f"The following key was not found in your configuration: {error}")

if ( not GOOD_CONFIG ) or ( not args.configuration ):
    BAUD_RATE = args.baud
    PORT_NAME = args.port
    REPEAT_PRESSES = False
    AUTO_RECONNECT = True


if PORT_NAME:
    RECONNECT_COUNT = 0
    while AUTO_RECONNECT and (RECONNECT_COUNT < MAX_RECONNECTS or MAX_RECONNECTS == 0):
        try:
            RECONNECT_COUNT += 1

            log.debug(f"Attempting to open serial port '{PORT_NAME}' with baud '{BAUD_RATE}'")

            s = serial.Serial(PORT_NAME, BAUD_RATE ,timeout=1)
            log.info("Port Open successful, waiting for serial data...")
            RECONNECT_COUNT = 0

            while s.is_open:
                if s.in_waiting > 0:
                    try:
                        rxLine = s.read()
                        rxLineHex = rxLine.hex().lower()
                        log.debug(f"Input received: {rxLineHex}")
                        execute_cmd(s, rxLineHex)
                    except KeyError as error:
                        log.error(f"The following key was not found in your configuration: {error}")

        except serial.SerialException as error:
            log.error(f"Failed to open {PORT_NAME} as a serial port!")
            log.debug(error)
        except (IOError, OSError) as error:
            log.error("A communication error has occured, check your connection")
            log.debug(error)
        except KeyboardInterrupt:
            log.info("Exitting")
            sys.exit(0)
        finally:
            if 's' in locals():
                s.close()

        time.sleep(1)

else:
    log.error("No port supplied")
    try:
        log.info(f"Available ports: {list_ports()}")
    except EnvironmentError:
        log.info("Unsupported platform, unable to list available ports.")
