import os

import can

from carcan.driving import Driving
from carcan.id import ID
from carcan.steering import Steering


class CanInterface:

    @staticmethod
    def encode(num: int) -> list:
        first = num & 255
        second = (num >> 8) & 255
        return [first, second]

    def drive_message(self):
        steer = CanInterface.encode(self.desired_steering_angle)
        speed = CanInterface.encode(self.desired_velocity)
        return can.Message(arbitration_id=ID.command.drive, data=steer + speed + [0, 0, 0, 0])

    def recreate_task(self, msg):
        if self.drive_task is not None:
            self.drive_task.stop()
        self.drive_task = self.bus.send_periodic(self.drive_message(), 0.02)

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

        self.drive_task = self.bus.send_periodic(self.drive_message(), 0.02)

    def steer(self, degree: int):
        self.desired_steering_angle = degree

    def move(self, speed: int):
        self.desired_velocity = speed
