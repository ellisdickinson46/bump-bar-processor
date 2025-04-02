import argparse
import os

from _helpers.configuration import CommandParser
from _helpers.logger import create_logger
from _helpers.processor import BumpBarProcessor


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog=os.path.basename(__file__),
    )
    subparsers = parser.add_subparsers(dest="command", )
    subparsers.required = True

    # 'run' command
    run_parser = subparsers.add_parser(
        'run',
        help='run the processor',
        usage="%(prog)s [-h] -b BAUD -p PORT [-a] [-r]"
    )
    run_parser.add_argument("-b", "--baud", type=int, default=1200, help="set baud rate (defaults to 1200)")
    run_parser.add_argument("-p", "--port", help="set serial port name/path", required=True)
    run_parser.add_argument("-a", action='store_true', help="enable auto-reconnect on disconnection")
    run_parser.add_argument("-r", action='store_true', help="enable repeat presses")

    # 'run-config' command
    from_conf_parser = subparsers.add_parser(
        'run-config',
        help='run the processor from a configuration file',
        usage="%(prog)s CONFIG_FILE"
    )
    from_conf_parser.add_argument('config_file', help='path to configuration file')

    list_ports = subparsers.add_parser(
        'list-ports',
        help="list available serial ports"
    )

    args = parser.parse_args()

    logger = create_logger("processor", "DEBUG")
    conf = CommandParser(logger, args)
    match conf.cmd_result.get("type", None):
        case "output":
            print(conf.cmd_result.get("return", None))
        case "launch":
            processor = BumpBarProcessor(logger, conf.cmd_result.get("parameters", {}))
        case _:
            logger.error("Unknown response type received from command parser")
