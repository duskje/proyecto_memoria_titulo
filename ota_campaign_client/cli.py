import os
import sys
import json

import click
import requests
from requests import HTTPError, ConnectionError as RequestsConnectionError

from loguru import logger

from device_info import DeviceConfig
import constants

logger.remove()
logger.add(sys.stdout, colorize=True, format="[{time}] <level>{message}</level>")


@click.group()
def utils_cli():
    pass


@utils_cli.command('write')
@click.option('--key', help='Key to write in config')
@click.option('--value', help='Value to write in config')
def write(key, value):
    if not os.path.exists(constants.CLIENT_CONFIG_DIR):
        os.makedirs(constants.CLIENT_CONFIG_DIR)

    if not os.path.exists(constants.CLIENT_CONFIG_PATH):
        logger.info('Config file not found, creating one...')
        DeviceConfig().to_yaml(constants.CLIENT_CONFIG_PATH) # write empty device config as default

    device_config = DeviceConfig.from_yaml(constants.CLIENT_CONFIG_PATH)
    device_config.write(key, value)

    device_config.to_yaml(constants.CLIENT_CONFIG_PATH)  # write empty device config as default
    logger.info(f'Wrote key value pair to config, result: {device_config}')


@utils_cli.command('register')
def register():
    if not os.path.exists(constants.CLIENT_CONFIG_DIR):
        logger.error('Could not find config.yaml')
        return

    if not os.path.exists(constants.CLIENT_CONFIG_PATH):
        logger.error('Could not find config.yaml')
        return

    device_config = DeviceConfig.from_yaml(constants.CLIENT_CONFIG_PATH)
    device_registration_url = f'http://{device_config.ota_campaign_address}/device'

    try:
        response = requests.post(device_registration_url, data=json.dumps(device_config.as_dict()))
        response.raise_for_status()
    except RequestsConnectionError:
        logger.error('Could not connect to server')
    except HTTPError as e:
        logger.error(f'Could not register. Got status code {e.response.status_code}')


if __name__ == '__main__':
    utils_cli()