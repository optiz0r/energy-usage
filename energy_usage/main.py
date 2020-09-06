import argparse
import logging
import os
import queue
import sys

import confuse

from energy_usage.influx_client import InfluxClient
from energy_usage.mqtt_client import MqttClient
from energy_usage.sep import parse_sep, usage_to_datapoints


def parse_args(arg_str=None):
    if arg_str is None:
        arg_str = sys.argv[1:]

    parser = argparse.ArgumentParser('energy-usage')

    parser.add_argument(
        '-d', '--debug', dest='debug', action='store_true',
        help='Enable debug output')
    parser.add_argument(
        '-n', '--noop', dest='noop', action='store_true',
        help="Don't make any modifications, just show what would be done")

    args = parser.parse_args(arg_str)

    return parser.prog, args


def load_config(args):
    config = confuse.Configuration('energy-usage', 'energy_usage')
    config.set_args(args)

    validate_config(config)

    return config


def validate_config(config):
    required = [
        (config['mqtt']['username'], str),
        (config['mqtt']['password'], str),
        (config['mqtt']['topic'], str)
    ]

    for item in required:
        key, datatype = item
        key.get(datatype)


def setup_logging(prog, config):
    logger = logging.getLogger()

    if config['debug'].get(bool):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('{0}[{1}]: %(levelname)s %(message)s'.format(prog, str(os.getpid())))
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def main():
    prog, args = parse_args()

    config = load_config(args)

    logger = setup_logging(prog, config)

    msg_q = queue.Queue()

    mqtt_client = MqttClient(
        server=config['mqtt']['server'].get(str),
        port=config['mqtt']['port'].get(int),
        username=config['mqtt']['username'].get(str),
        password=config['mqtt']['password'].get(str),
        topic=config['mqtt']['topic'].get(str),
        ca_certs=config['ca_certs'].get(str),
        msg_q=msg_q)
    mqtt_client.connect()
    mqtt_client.run()

    influx_client = InfluxClient(
        server=config['influx']['server'].get(str),
        port=config['influx']['port'].get(int),
        database='default',
    )

    while True:
        try:
            msg = msg_q.get()
            logger.debug(msg.topic + " " + str(msg.payload))
            usage = parse_sep(msg.topic, msg.payload)
            if usage:
                usage_datapoints = usage_to_datapoints(usage)
                if not config["noop"].get(bool):
                    influx_client.write_points(usage_datapoints)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
