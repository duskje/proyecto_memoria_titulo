import os
import asyncio
import json
from collections import deque

import tornado

from dotenv import load_dotenv
from loguru import logger

import constants
from entities import Device, Rollout
from dto import RolloutDTO

load_dotenv()


class FullRolloutQueueError(Exception):
    pass

class DeviceNotRegisteredError(Exception):
    pass


class OTACampaign:
    def __init__(self, cond: tornado.locks.Condition):
        self.cond = cond

        self.device_registration_by_id = {}
        self.device_registration_by_tag = {}

        self.package_registry = []
        self.rollout_queue = deque()
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

    def _new_rollout(self, device_id: str, package_version: str, package_name: str):
        current_rollout_id = self.rollout_id
        self.rollout_id += 1
        return Rollout(id=current_rollout_id,
                       device_id=device_id,
                       package_version=package_version,
                       package_name=package_name)

    def add_to_rollout_queue_by_id(self, device_id: str, package_version: str, package_name: str):
        new_rollout = self._new_rollout(device_id, package_version, package_name)
        self.rollout_queue.append(new_rollout)

        if len(self.rollout_queue) > constants.ROLLOUT_QUEUE_SIZE:
            raise FullRolloutQueueError('Rollout queue is full')

        self.cond.notify_all()

    def add_to_rollout_queue_by_tag(self, device_tag: str, package_version: str, package_name: str):
        for device in self.device_registration_by_tag[device_tag]:
            self.add_to_rollout_queue_by_id(device.id, package_version, package_name)

    def rollout(self, device_id: str):
        if self.device_registration_by_id.get(device_id) is None:
            raise DeviceNotRegisteredError(f'Could not find device with id "{device_id}"')

        if not self.rollout_queue:
            return None

        if self.rollout_queue[0].device_id != device_id:
            return None

        return self.rollout_queue.popleft()


class DeviceConnectionManager:
    def __init__(self, cond: tornado.locks.Condition):
        self.cond = cond
        self.wait_until_dropped_cond = tornado.locks.Condition()
        self.semaphore = tornado.locks.Semaphore()

        self.connected_devices = set()
        self.devices_to_drop = set()

    async def add_connection(self, device_id: str):
        await self.semaphore.acquire()

        if device_id in self.connected_devices:
            self.devices_to_drop.add(device_id)
            self.cond.notify_all()
            await self.wait_until_dropped_cond.wait()

        self.connected_devices.add(device_id)

        self.semaphore.release()

    def drop(self, device_id: str):
        in_drop_list = device_id in self.devices_to_drop

        if in_drop_list:
            self.devices_to_drop.remove(device_id)

            self.connected_devices.remove(device_id)
            self.wait_until_dropped_cond.notify(1)

        return in_drop_list

    def disconnect(self, device_id: str):
        self.connected_devices.remove(device_id)


rollout_cond = tornado.locks.Condition()
global_ota_campaign = OTACampaign(rollout_cond)
global_device_connection_manager = DeviceConnectionManager(rollout_cond)


class OTACampaignRegistration(tornado.web.RequestHandler):
    def post(self):
        device_data = json.loads(self.request.body)

        device_data = dict(device_data)
        tags = device_data.get('tags')

        device = Device(id=device_data.get('id'),
                        tags=tuple(tags) if tags is not None else tuple())

        logger.info(f'Got device "{device}" from address {self.request.remote_ip}')

        global_ota_campaign.register_device(device)

        logger.info(f'Device "{device}" was registered successfully')


class OTACampaignListRegisteredDevices(tornado.web.RequestHandler):
    def get(self):
        return self.write(json.dumps([device.json() for device in global_ota_campaign.device_registration_by_id.values()]))


class OTACampaignRollout(tornado.web.RequestHandler):
    def post(self):
        request_json = json.loads(self.request.body)
        try:
            rollout_dto = RolloutDTO.from_json(request_json)
        except KeyError as e:
            raise tornado.web.HTTPError(status_code=400, log_message=str(e))

        for device_id in rollout_dto.device_ids:
            logger.info(f'Device "{device_id}" sent to the rollout queue')
            global_ota_campaign.add_to_rollout_queue_by_id(device_id,
                                                           rollout_dto.commit,
                                                           rollout_dto.package_name)


class OTACampaignUpdateListener(tornado.web.RequestHandler):
    async def get(self):
        try:
            device_id = json.loads(self.request.body)['device_id']
            await global_device_connection_manager.add_connection(device_id)
        except KeyError:
            raise tornado.web.HTTPError(status_code=400, log_message="'device_id' key missing")

        logger.info(f'Device {device_id} listening for updates')

        try:
            rollout = global_ota_campaign.rollout(device_id)
        except DeviceNotRegisteredError:
            raise tornado.web.HTTPError(status_code=400, log_message=f"Device '{device_id}' not registered")

        while not rollout:
            wait_future = global_ota_campaign.cond.wait()

            try:
                await wait_future
            except asyncio.CancelledError:
                global_device_connection_manager.drop(device_id)
                logger.info(f'Device {device_id} disconnected')
                return

            if global_device_connection_manager.drop(device_id):
                logger.info(f'Last connection for {device_id} dropped')
                return

            rollout = global_ota_campaign.rollout(device_id)

        global_device_connection_manager.disconnect(device_id)
        logger.info(f'Closing connection for "{device_id}"')

        logger.info(f'Sending rollout "{rollout}" to "{device_id}"')

        return self.write(rollout.json())


async def main():
    try:
        port = int(os.getenv('PORT'))
    except TypeError:
        logger.error('No port found at .env')
        return

    logger.info(f'Running server at port {port}')

    app = tornado.web.Application(
        [
            ('/device', OTACampaignRegistration),
            ('/devices', OTACampaignListRegisteredDevices),
            ('/listen_for_updates', OTACampaignUpdateListener),
            ('/rollout', OTACampaignRollout),
        ]
    )

    app.listen(port)
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())