import json

from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    id: str # guid
    # address: str
    tags: tuple[str]

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


@dataclass(frozen=True)
class Rollout:
    id: int
    device_id: str
    package_version: str
    package_name: str

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
