import json

from device_info import DeviceConfig
import constants

from loguru import logger
from dotenv import load_dotenv
import requests
from requests import ReadTimeout

from ota_campaign_client.flatpak import Flatpak


def main():
    load_dotenv()

    try:
        device_config = DeviceConfig.from_yaml(constants.CLIENT_CONFIG_PATH)
    except FileNotFoundError:
        logger.error('Config file not found')
        return

    flatpak = Flatpak()

    logger.info(f'Device ID: {device_config.id}')

    while True:
        logger.info('Checking if there is a new rollout from OTA Campaign server...')

        rollout_url = f'http://{device_config.ota_campaign_address}/listen_for_updates'

        try:
            response = requests.get(rollout_url,
                                    data=json.dumps({'device_id': device_config.id}),
                                    timeout=constants.LONG_POLL_TIMEOUT)
            response.raise_for_status()
        except ReadTimeout:
            logger.debug("Timed out, listening again...")
            continue

        response_json = json.loads(response.content)

        logger.info(f'Executing update (package_name={response_json["package_name"]}, commit={response_json["commit"]})')
        flatpak.execute_update(package_name=response_json['package_name'], commit=response_json['commit'])



if __name__ == '__main__':
    main()
