import os
from typing import List

import can

from carcan.driving import Driving
from carcan.id import ID
from carcan.listener import CanListener
from carcan.steering import Steering


class CanInterface:

    @staticmethod
    def encode(num: int) -> List[int]:
        first = num & 255
        second = (num >> 8) & 255
        return [first, second]

    def _drive_message(self) -> can.Message:
        steer = CanInterface.encode(self._desired_steering_angle)
        speed = CanInterface.encode(self._desired_velocity)
        return can.Message(arbitration_id=ID.command.drive, data=steer + speed + [0, 0, 0, 0])

    def _create_task(self) -> can.CyclicSendTaskABC:
        return self._bus.send_periodic(self._drive_message(), 0.02)

    def _recreate_task(self) -> None:
        if self._drive_task is not None:
            self._drive_task.stop()
        self._drive_task = self._create_task()

    def _set_current_steering_angle(self, new_val: int) -> None:
        self._steering_angle = new_val

    def _set_current_velocity(self, new_val: int) -> None:
        self._velocity = new_val

    def _create_listener(self) -> CanListener:
        return CanListener(steer_setter=self._set_current_steering_angle,
                           velocity_setter=self._set_current_velocity)

    def __init__(self, interface=None, channel=None, bitrate=None):
        default_conf = can.util.load_config()
        bustype = interface if interface else default_conf['interface']
        channel = channel if channel else default_conf['channel']
        bitrate = bitrate if bitrate is not None else default_conf['bitrate']

        listeners = [self._create_listener()]
        if os.getenv('CAN_DEBUG'):
            listeners.append(can.Printer())

        self._bus = can.interface.Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        self._notifier = can.Notifier(self._bus, listeners)

        self._desired_steering_angle = Steering.neutral
        self._desired_velocity = Driving.neutral

        self._steering_angle = 0
        self._velocity = 0

        self._drive_task = self._create_task()

    def steer(self, degree: int) -> None:
        self._desired_steering_angle = degree
        self._recreate_task()

    def move(self, speed: int) -> None:
        self._desired_velocity = speed
        self._recreate_task()

    def stop(self) -> None:
        self._bus.shutdown()

    @property
    def steering_angle(self) -> int:
        return self._steering_angle

    @property
    def velocity(self) -> int:
        return self._velocity
