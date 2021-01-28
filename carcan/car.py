from threading import Lock
from typing import Union

import can

from tx_message import DriveMessage, CheckMessage
from transmitter import Transmitter
from receiver import Receiver
from car_data import CarData
from driving import Driving
from steering import Steering


class Car:
    def __init__(self):
        self.drive_msg = DriveMessage()
        self.check_msg = CheckMessage()
        self._bus = can.interface.Bus(bustype='socketcan', channel='can0')
        self.transmitter = Transmitter(self._bus)
        self.receiver = Receiver(self._bus, self.update)
        self.data = CarData()

        self.lock = Lock()

    def locked(self, fun):
        def perform_locked(*args, **kwargs):
            try:
                self.lock.acquire()
                fun(*args, **kwargs)
            finally:
                self.lock.release()

        return perform_locked

    def update(self, data: CarData):
        self.data = data
        self.tx_check(data.rx_check)
        self.periodic_update()

    @locked
    def periodic_update(self):
        self.drive_msg.increment_msg_count()
        self.check_msg.increment_msg_count()
        self.send_messages()

    def send_messages(self):
        if self.drive_msg is not None:
            self.transmitter.transmit(self.drive_msg)
        if self.check_msg is not None:
            self.transmitter.transmit(self.check_msg)

    @locked
    def set_velocity(self, velocity: Union[int, float]) -> None:
        self.drive_msg.velocity = Driving.to_can(int(velocity))

    @locked
    def set_acceleration(self, acceleration: int) -> None:
        self.drive_msg.acceleration_level = acceleration

    @locked
    def set_steering(self, steering: Union[int, float]) -> None:
        self.drive_msg.steering = Steering.to_can(int(steering))

    @locked
    def set_steering_precision(self, precision: int) -> None:
        self.drive_msg.steering_level = precision

    @locked
    def release_control(self) -> None:
        self.drive_msg.ctrl = 0

    @locked
    def tx_check(self, rx_check: int) -> None:
        self.check_msg.set_tx_check(rx_check)
