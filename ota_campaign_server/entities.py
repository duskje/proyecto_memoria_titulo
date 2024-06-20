import json

from dataclasses import dataclass


@dataclass(frozen=True)
class Device:
    id: str # guid
    address: str
    tags: tuple[str]

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)


@dataclass(frozen=True)
class Rollout:
    id: int
    device_id: int
    package_version: str

    def json(self):
        return json.dumps(self, default=lambda o: o.__dict__)
