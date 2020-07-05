import os

import can

from carcan.driving import Driving
from carcan.id import ID
from carcan.steering import Steering


class CanInterface:

    def encode(self, num: int) -> list:
        first = num & 255
        second = (num >> 8) & 255
        return [first, second]

    def drive_message(self):
        speed = self.encode(Driving.neutral/2)
        steer = self.encode(Steering.left_max)
        return can.Message(arbitration_id=ID.command.drive, data=speed + steer + [0, 0, 0, 0])

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

        self.desired_steering_angle = 0
        self.desired_velocity = 0

        self.drive_task = self.bus.send_periodic(self.drive_message(), 0.02)

    def steer(self, degree: float):
        pass
