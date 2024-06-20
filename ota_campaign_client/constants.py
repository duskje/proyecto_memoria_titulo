import os
from xdg_base_dirs import xdg_config_home

CLIENT_CONFIG_DIR = os.path.join(xdg_config_home(), 'ota_campaign_client')
CLIENT_CONFIG_PATH = os.path.join(CLIENT_CONFIG_DIR, 'config.yaml')
