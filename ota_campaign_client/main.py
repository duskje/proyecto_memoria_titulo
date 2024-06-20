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
        list_devices = f'http://{device_config.ota_campaign_address}/devices'
        print(requests.get(list_devices))

        logger.info('Polling from OTA Campaign server...')


if __name__ == '__main__':
    main()
