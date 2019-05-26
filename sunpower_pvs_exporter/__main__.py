# -*- coding: utf-8 -*-
"""
sunpower_pvs_exporter CLI/main entrypoint
"""

import argparse
import logging
import time

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

from sunpower_pvs_exporter.exporter import SunPowerPVSupervisorCollector


def create_parser():
    """
    Build an argument parser for CLI options
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--hostname",
                        default="sunpowerconsole.com",
                        help="SunPower PV Supervisor hostname",
                       )

    parser.add_argument("--port",
                        default=80,
                        help="SunPower PV Supervisor port",
                       )

    parser.add_argument("--use-tls",
                        action="store_const",
                        const=True,
                        default=False,
                        help="Use SSL/TLS when communicating with SunPower PV "
                             "Supervisor",
                       )

    parser.add_argument("--listen-on",
                        default=9110,
                        type=int,
                        help="Listen on the specified port"
                       )

    parser.add_argument("--log-file",
                        default=None,
                        help="Output logfile",
                       )

    parser.add_argument("--log-level",
                        default="INFO",
                        choices=["ERROR", "WARNING", "INFO", "DEBUG"],
                        help="Log level",
                       )

    parser.add_argument("--timeout",
                        default=10,
                        type=int,
                        help="Connection timeout value (in seconds)"
                       )

    parser.add_argument("--use-device-data-timestamp",
                        default=False,
                        action="store_const",
                        const=True,
                        help="Use the data timestamp from the PVS device",
                       )

    return parser


def main():
    """
    Main method
    """
    args = create_parser().parse_args()

    log_format = '%(asctime)s %(message)s'
    logging_args = dict(format=log_format,
                        level=args.log_level)
    if args.log_file:
        logging_args['filename'] = args.log_file
        logging_args['filemode'] = 'a'

    logging.basicConfig(**logging_args)

    scheme = "https" if args.use_tls else "http"
    use_ts = args.use_device_data_timestamp
    collector = SunPowerPVSupervisorCollector(hostname=args.hostname,
                                              port=args.port,
                                              scheme=scheme,
                                              timeout=args.timeout,
                                              use_device_data_timestamp=use_ts,
                                             )

    logging.info("Listening on port %d...", args.listen_on)
    start_http_server(args.listen_on)

    REGISTRY.register(collector)

    # Sleep indefinitely until we receive a signal
    while True:
        time.sleep(10)


if __name__ == '__main__':
    main()
