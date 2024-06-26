from typing import Optional

import requests
from requests import HTTPError, ConnectionError as RequestsConnectionError
import click

import json

from loguru import logger


@click.group()
def utils_cli():
    pass


@utils_cli.command('register', help='Register device')
@click.option('--ota-campaign-address', default='100.78.173.50:3636', help="OTA server address")
@click.option('--device-id', help="GUID of the device", required=True)
@click.option('--tags', default=None, help="Additional tags to identify the device")
def register(ota_campaign_address: str, device_id: str, tags: Optional[str]):
    device_registration_url = f'http://{ota_campaign_address}/device'

    device_registration_data = {
        'id': device_id,
        'tags': tags.split(',') if tags is not None else [],
    }

    try:
        response = requests.post(device_registration_url, data=json.dumps(device_registration_data))
        response.raise_for_status()
    except RequestsConnectionError:
        logger.error('Could not connect to server')
    except HTTPError as e:
        logger.error(f'Could not register. Got status code {e.response.status_code}')


if __name__ == '__main__':
    utils_cli()