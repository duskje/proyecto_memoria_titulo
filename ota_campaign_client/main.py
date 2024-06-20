import json

from device_info import DeviceConfig
import constants

from loguru import logger
from dotenv import load_dotenv
import requests


def main():
    load_dotenv()

    try:
        device_config = DeviceConfig.from_yaml(constants.CLIENT_CONFIG_PATH)
    except FileNotFoundError:
        logger.error('Config file not found')
        return

    while True:
        logger.info('Checking if there is a new rollout from OTA Campaign server...')

        rollout_url = f'http://{device_config.ota_campaign_address}/listen_for_updates'

        response = requests.get(rollout_url, data=json.dumps({'device_id': device_config.id}))
        response.raise_for_status()

        logger.debug(response.content)


if __name__ == '__main__':
    main()
