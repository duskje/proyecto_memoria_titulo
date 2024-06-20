import time
import os

from packaging.rpm import RPM

from loguru import logger

from dotenv import load_dotenv


def main():
    load_dotenv()
    polling_interval_secs = float(os.getenv('POLLING_INTERVAL_SECS'))

    while True:
        logger.info('Polling from OTA Campaign server...')
        time.sleep(polling_interval_secs)

    # logger.debug(RPM().get_current_package_version('openssl'))


if __name__ == '__main__':
    main()
