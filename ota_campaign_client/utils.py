import os.path

from device_info import DeviceConfig
import constants

import click


@click.command()
@click.option('--key', help='Key to write in config')
@click.option('--value', help='Value to write in config')
def utils_cli(key, value):
    if not os.path.exists(constants.CLIENT_CONFIG_DIR):
        os.makedirs(constants.CLIENT_CONFIG_DIR)

    if not os.path.exists(constants.CLIENT_CONFIG_PATH):
        DeviceConfig().to_yaml(constants.CLIENT_CONFIG_PATH) # write empty device config as default

    device_config = DeviceConfig.from_yaml(constants.CLIENT_CONFIG_PATH)
    device_config.write(key, value)

    device_config.to_yaml(constants.CLIENT_CONFIG_PATH)  # write empty device config as default

if __name__ == '__main__':
    utils_cli()