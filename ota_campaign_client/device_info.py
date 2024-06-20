from dataclasses import dataclass, asdict, fields
from typing import Optional
import yaml


@dataclass
class DeviceConfig:
    id: Optional[str] = None
    hardware_id: Optional[str] = None
    address: Optional[str] = None
    auth_token: Optional[str] = None
    ota_campaign_address: Optional[str] = None

    tags: Optional[list[str]] = None

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            yaml_data = yaml.load(f, Loader=yaml.Loader).get('device_config')

        return cls(**yaml_data)

    def to_yaml(self, path: str):
        with open(path, 'w') as f:
            yaml.dump({'device_config': asdict(self)}, f)

    def write(self, key: str, value: any):
        available_keys = asdict(self).keys()

        if key not in available_keys:
            raise KeyError(f"There is no key {key}, available: {available_keys}")

        setattr(self, key, value)

    def as_dict(self):
        return asdict(self)
