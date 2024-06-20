from dataclasses import dataclass

import asyncio
import json

import tornado

from loguru import logger


@dataclass(frozen=True)
class Device:
    id: int
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


class OTACampaign:
    def __init__(self):
        self.device_registration_by_id = {}
        self.device_registration_by_tag = {}

        self.package_registry = []
        self.rollout_queue = []
        self.rollout_id = 0

    def add_package_to_registry(self):
        pass

    def register_device(self, device: Device):
        self.device_registration_by_id[device.id] = device

        for device_tag in device.tags:
            tags = self.device_registration_by_tag.get(device_tag)

            if tags is None:
                self.device_registration_by_tag[device_tag] = {device}
            else:
                self.device_registration_by_tag[device_tag].add(device)

    def add_to_rollout_queue_by_id(self, device_id: int, package_version: str):
        device = self.device_registration_by_id[device_id]

        rollout = Rollout(id=self.rollout_id,
                          device_id=device.id,
                          package_version=package_version)

        self.rollout_queue.append(rollout)
        self.rollout_id += 1

    def add_to_rollout_queue_by_tag(self, device_tag: str, package_version: str):
        for device in self.device_registration_by_tag[device_tag]:
            rollout = Rollout(id=self.rollout_id,
                              device_id=device.id,
                              package_version=package_version)

            self.rollout_queue.append(rollout)
            self.rollout_id += 1


global_ota_campaign = OTACampaign()


class OTACampaignRegistration(tornado.web.RequestHandler):
    def post(self):
        device_data = json.loads(self.request.body)

        device_data = dict(device_data)

        device = Device(id=device_data.get('id'),
                        address=device_data.get('address'),
                        tags=tuple(device_data.get('tags')))

        logger.info(f'Got device "{device}"')

        global_ota_campaign.register_device(device)
        logger.info(f'Device "{device}"  was registered successfully')


class OTACampaignListRegisteredDevices(tornado.web.RequestHandler):
    def get(self):
        return self.write(json.dumps([device.json() for device in global_ota_campaign.device_registration_by_id.values()]))

class OTACampaignRollout:
    def get(self):
        pass


async def main():
    app = tornado.web.Application(
        [
            ('/device', OTACampaignRegistration),
            ('/devices', OTACampaignListRegisteredDevices)
        ]
    )
    app.listen(5000)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())