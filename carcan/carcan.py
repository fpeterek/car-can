import os

import can

from carcan.driving import Driving
from carcan.id import ID
from carcan.listener import CanListener
from carcan.steering import Steering


class CanInterface:

    def _drive_message(self) -> can.Message:
        steer = self._desired_steering_angle
        speed = self._desired_velocity
        return can.Message(arbitration_id=ID.command.drive, data=[steer, speed])

    def _create_drive_task(self) -> can.CyclicSendTaskABC:
        return self._send_periodic(self._drive_message())

    def _create_check_task(self) -> can.CyclicSendTaskABC:
        return self._send_periodic(self._create_check_message())

    def _send_periodic(self, msg: can.Message):
        return self._bus.send_periodic(msg=msg, period=0.05)

    def _recreate_drive_task(self) -> None:
        if self._drive_task is not None:
            self._drive_task.stop()
        self._drive_task = self._create_drive_task()

    def _recreate_check_task(self) -> None:
        if self._check_task is not None:
            self._check_task.stop()
        self._check_task = self._create_check_task()

    def _set_driving_info(self, steer: int, speed: int, ctrl: bool) -> None:
        self._steering_angle = steer
        self._velocity = speed
        self._has_control = ctrl

    def _set_check(self, ok: bool):
        self._ok = ok
        if not ok:
            self._recreate_check_task()

    @staticmethod
    def _create_status_message() -> can.Message:
        online = 1
        ctrl = 1
        return can.Message(arbitration_id=ID.command.status, data=[online, ctrl])

    @property
    def is_ok(self):
        return self._ok and self._has_control

    def _create_check_message(self) -> can.Message:
        stop = int(not self.is_ok)
        tx_check = 255
        return can.Message(arbitration_id=ID.command.check, data=[stop, tx_check])

    def _create_listener(self) -> CanListener:
        return CanListener(check_setter=self._set_check,
                           driving_info_setter=self._set_driving_info)

    def __init__(self, interface=None, channel=None, bitrate=None):
        default_conf = can.util.load_config()
        bustype = interface if interface else default_conf['interface']
        channel = channel if channel else default_conf['channel']
        bitrate = bitrate if bitrate else default_conf['bitrate']

        listeners = [self._create_listener()]
        if os.getenv('CAN_DEBUG'):
            listeners.append(can.Printer())

        self._bus = can.interface.Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        self._notifier = can.Notifier(self._bus, listeners)

        self._desired_steering_angle = Steering.neutral
        self._desired_velocity = Driving.neutral

        self._steering_angle = 0
        self._velocity = 0
        self._has_control = True
        self._ok = True

        self._drive_task = self._create_drive_task()
        self._status_task = self._send_periodic(self._create_status_message())
        self._check_task = self._create_check_task()

    def steer(self, degree: int) -> None:
        self._desired_steering_angle = Steering.to_can(degree)
        self._recreate_drive_task()

    def move(self, speed: int) -> None:
        self._desired_velocity = Driving.to_can(speed)
        self._recreate_drive_task()

    def stop(self) -> None:
        self._bus.shutdown()

    @property
    def steering_angle(self) -> int:
        return Steering.to_value(self._steering_angle)

    @property
    def velocity(self) -> int:
        return Driving.to_value(self._velocity)
