from dataclasses import dataclass
from typing import Optional
import yaml


@dataclass
class DeviceConfig:
    hardware_id: Optional[str]
    address: Optional[str]
    auth_token: Optional[str]
    ota_campaign_address: Optional[str]

    @staticmethod
    def from_yaml(path: str):
        with open(path, 'r') as f:
            print(yaml.load(f, Loader=yaml.Loader))