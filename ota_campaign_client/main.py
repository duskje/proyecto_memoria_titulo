from packaging.rpm import RPM

from loguru import logger


def main():
    logger.debug(RPM().get_current_package_version('openssl'))


if __name__ == '__main__':
    main()
