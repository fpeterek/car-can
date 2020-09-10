import os
import time
from threading import Lock

import can
import gpsd

from driving import Driving
from id import ID
from listener import CanListener
from steering import Steering


def env_is_true(env: str) -> bool:
    return os.getenv(env) and os.getenv(env).lower() in ('true', '1')


class CarInterface:

    @property
    def _time_ms(self):
        return time.time_ns() / 1_000_000

    @property
    def _drive_message(self) -> can.Message:
        steer = self._desired_steering_angle
        speed = self._desired_velocity
        return can.Message(arbitration_id=ID.command.drive, data=[steer, speed, 0, 0, 0, 0, 0, 0], is_extended_id=False)

    def _create_drive_task(self) -> can.ModifiableCyclicTaskABC:
        return self._send_periodic(self._drive_message)

    def _create_check_task(self) -> can.ModifiableCyclicTaskABC:
        return self._send_periodic(self._check_message)

    def _create_status_task(self) -> can.ModifiableCyclicTaskABC:
        return self._send_periodic(self._create_status_message(request_control=True))

    def _send_periodic(self, msg: can.Message) -> can.ModifiableCyclicTaskABC:
        return self._bus.send_periodic(msg=msg, period=0.05)

    def _modify_drive_task(self) -> None:
        if self._check_task is not None:
            self._drive_task.modify_data(self._drive_message)

    def _modify_check_task(self) -> None:
        if self._check_task is not None:
            self._check_task.modify_data(self._check_message)

    def _shutdown_status_task(self) -> None:
        if self._status_task is not None:
            self._status_task.modify_data(self._create_status_message(request_control=False))

    def _set_driving_info(self, steer: int, speed: int, ctrl: bool) -> None:
        if self._debug:
            print(f"Received info (steer={steer}, v={speed}, c={ctrl})")
        self._steering_angle = steer
        self._velocity = speed
        self._has_control = ctrl

    def _set_check(self, rx_check: int) -> None:
        if self._debug:
            print(f"Received check ({rx_check})")
        self._check_lock.acquire()
        self._tx_check = (rx_check + 1) % 256
        self._modify_check_task()
        self._check_lock.release()

    @staticmethod
    def _create_status_message(request_control: bool) -> can.Message:
        online = 1
        ctrl = int(request_control)
        return can.Message(arbitration_id=ID.command.status,
                           data=[online, ctrl, 0, 0, 0, 0, 0, 0],
                           is_extended_id=False)

    @property
    def is_ok(self) -> bool:
        return self._has_control and (self._time_ms - self._check_received) < self._check_threshold

    @property
    def ebrake_enabled(self) -> bool:
        return self._ebrake

    @property
    def _check_message(self) -> can.Message:
        stop = int(self._ebrake)
        tx_check = self._tx_check
        return can.Message(arbitration_id=ID.command.check,
                           data=[stop, tx_check, 0, 0, 0, 0, 0, 0],
                           is_extended_id=False)

    def _create_listener(self) -> CanListener:
        return CanListener(check_setter=self._set_check, driving_info_setter=self._set_driving_info)

    def __init__(self, interface=None, channel=None):
        # default_conf = can.util.load_config()
        bustype = interface  # if interface else default_conf['interface']
        channel = channel  # if channel else default_conf['channel']
        # bitrate = bitrate if bitrate else default_conf['bitrate']

        self._debug = env_is_true('CAN_DEBUG')

        listeners = [self._create_listener()]
        if env_is_true('CAN_PRINTER'):
            listeners.append(can.Printer())

        gpsd.connect()

        self._bus = can.interface.Bus(bustype=bustype, channel=channel)
        self._notifier = can.Notifier(self._bus, listeners)

        self._desired_steering_angle = Steering.can_offset
        self._desired_velocity = Driving.can_offset

        self._steering_angle = 0
        self._velocity = 0
        self._tx_check = 0
        self._check_received = self._time_ms
        self._check_threshold = 50 + 20  # 50 ms message cycle plus 20 ms extra
        self._has_control = True
        self._ebrake = False

        self._check_lock = Lock()

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
        self._modify_drive_task()

    def move(self, speed: int) -> None:
        self._desired_velocity = Driving.to_can(speed)
        self._modify_drive_task()

    def drive(self, velocity: int, steering_degree: int) -> None:
        self._desired_velocity = Driving.to_can(velocity)
        self._desired_steering_angle = Steering.to_can(steering_degree)
        self._modify_drive_task()

    def stop(self) -> None:
        self.move(Driving.zero)

    def set_ebrake(self, brake: bool) -> None:
        self._check_lock.acquire()
        self._ebrake = brake
        self._modify_check_task()
        self._check_lock.release()

    def forward(self) -> None:
        self.steer(Steering.neutral)

    def shutdown(self) -> None:
        if self._drive_task is not None:
            self._drive_task.stop()
        if self._status_task is not None:
            # Return control before shutting down
            self._shutdown_status_task()
            time.sleep(0.2)
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

    @property
    def gps_position(self):
        pos = gpsd.get_current().position()
        print(pos)
        return pos  # gpsd.get_current().position()

