import os
import time

import can

from driving import Driving
from id import ID
from listener import CanListener
from steering import Steering


def env_is_true(env: str) -> bool:
    return os.getenv(env) and os.getenv(env).lower() in ('true', '1')


class CarInterface:

    def _drive_message(self) -> can.Message:
        steer = self._desired_steering_angle
        speed = self._desired_velocity
        return can.Message(arbitration_id=ID.command.drive, data=[steer, speed, 0, 0, 0, 0, 0, 0], is_extended_id=False)

    def _create_drive_task(self) -> can.CyclicSendTaskABC:
        return self._send_periodic(self._drive_message())

    def _create_check_task(self) -> can.CyclicSendTaskABC:
        return self._send_periodic(self._create_check_message())

    def _create_status_task(self) -> can.CyclicSendTaskABC:
        return self._send_periodic(self._create_status_message())

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

    def _check(self) -> None:
        if not self.is_ok:
            self._desired_steering_angle = Steering.can_offset
            self._desired_velocity = Driving.can_offset
            self._drive_task.stop()
            self._drive_task = None
            while not self.is_ok:
                time.sleep(0.02)
            self._recreate_drive_task()

    def _set_driving_info(self, steer: int, speed: int, ctrl: bool) -> None:
        if self._debug:
            print(f"Received info (steer={steer}, v={speed}, c={ctrl})")
        self._steering_angle = steer
        self._velocity = speed
        self._has_control = ctrl
        self._check()

    def _set_check(self, ok: bool):
        if self._debug:
            print(f"Received check ({'ok' if ok else 'not ok'})")
        self._ok = ok
        self._check()

    @staticmethod
    def _create_status_message() -> can.Message:
        online = 1
        ctrl = 1
        return can.Message(arbitration_id=ID.command.status,
                           data=[online, ctrl, 0, 0, 0, 0, 0, 0],
                           is_extended_id=False)

    @property
    def is_ok(self):
        return self._ok and self._has_control

    def _create_check_message(self) -> can.Message:
        stop = int(not self.is_ok)
        tx_check = 255
        return can.Message(arbitration_id=ID.command.check,
                           data=[stop, tx_check, 0, 0, 0, 0, 0, 0],
                           is_extended_id=False)

    def _create_listener(self) -> CanListener:
        return CanListener(check_setter=self._set_check,
                           driving_info_setter=self._set_driving_info)

    def __init__(self, interface=None, channel=None):
        # default_conf = can.util.load_config()
        bustype = interface  # if interface else default_conf['interface']
        channel = channel  # if channel else default_conf['channel']
        # bitrate = bitrate if bitrate else default_conf['bitrate']

        listeners = [self._create_listener()]
        if env_is_true('CAN_PRINTER'):
            listeners.append(can.Printer())

        if env_is_true('CAN_DEBUG'):
            self._debug = True

        self._bus = can.interface.Bus(bustype=bustype, channel=channel)
        self._notifier = can.Notifier(self._bus, listeners)

        self._desired_steering_angle = Steering.can_offset
        self._desired_velocity = Driving.can_offset

        self._steering_angle = 0
        self._velocity = 0
        self._has_control = True
        self._ok = True

        self._status_task = None
        self._drive_task = None
        self._check_task = None

        self._status_task = self._create_status_task()
        time.sleep(0.2)
        self._drive_task = self._create_drive_task()
        self._check_task = self._create_check_task()
        time.sleep(0.2)

    def steer(self, degree: int) -> None:
        self._desired_steering_angle = Steering.to_can(degree)
        self._recreate_drive_task()

    def move(self, speed: int) -> None:
        self._desired_velocity = Driving.to_can(speed)
        self._recreate_drive_task()

    def drive(self, velocity: int, steering_degree: int) -> None:
        self._desired_velocity = Driving.to_can(velocity)
        self._desired_steering_angle = Steering.to_can(steering_degree)
        self._recreate_drive_task()

    def stop(self) -> None:
        self.move(Driving.zero)

    def forward(self) -> None:
        self.steer(Steering.neutral)

    def shutdown(self) -> None:
        if self._drive_task is not None:
            self._drive_task.stop()
        if self._status_task is not None:
            self._status_task.stop()
        if self._check_task is not None:
            self._check_task.stop()
        self._bus.shutdown()

    @property
    def steering_angle(self) -> int:
        return Steering.to_value(self._steering_angle)

    @property
    def velocity(self) -> int:
        return Driving.to_value(self._velocity)
