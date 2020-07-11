import os
from typing import List

import can

from carcan.driving import Driving
from carcan.id import ID
from carcan.steering import Steering


class CanInterface:

    @staticmethod
    def encode(num: int) -> List[int]:
        first = num & 255
        second = (num >> 8) & 255
        return [first, second]

    def drive_message(self) -> can.Message:
        steer = CanInterface.encode(self.desired_steering_angle)
        speed = CanInterface.encode(self.desired_velocity)
        return can.Message(arbitration_id=ID.command.drive, data=steer + speed + [0, 0, 0, 0])

    def create_task(self) -> can.CyclicSendTaskABC:
        return self.bus.send_periodic(self.drive_message(), 0.02)

    def recreate_task(self) -> None:
        if self.drive_task is not None:
            self.drive_task.stop()
        self.drive_task = self.create_task()

    def __init__(self, interface=None, channel=None, bitrate=None):
        default_conf = can.util.load_config()
        bustype = interface if interface else default_conf['interface']
        channel = channel if channel else default_conf['channel']
        bitrate = bitrate if bitrate is not None else default_conf['bitrate']

        listeners = []
        if os.getenv('CAN_DEBUG'):
            listeners.append(can.Printer())

        self.bus = can.interface.Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        self.notifier = can.Notifier(self.bus, listeners)

        self.desired_steering_angle = Steering.neutral
        self.desired_velocity = Driving.neutral

        self.drive_task = self.create_task()

    def steer(self, degree: int) -> None:
        self.desired_steering_angle = degree
        self.recreate_task()

    def move(self, speed: int) -> None:
        self.desired_velocity = speed
        self.recreate_task()
