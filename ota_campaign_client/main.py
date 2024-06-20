import json

from device_info import DeviceConfig
import constants

from loguru import logger
from dotenv import load_dotenv
import requests
from requests import ReadTimeout


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

        try:
            response = requests.get(rollout_url,
                                    data=json.dumps({'device_id': device_config.id}),
                                    timeout=constants.LONG_POLL_TIMEOUT)

            response.raise_for_status()

            logger.debug(response.content)
        except ReadTimeout:
            logger.info('Timed out, polling again...')



if __name__ == '__main__':
    main()
