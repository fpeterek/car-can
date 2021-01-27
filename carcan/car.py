from threading import Lock
from typing import Union

from tx_message import DriveMessage, CheckMessage
from transmitter import Transmitter
from driving import Driving
from steering import Steering


class Car:
    def __init__(self):
        self.drive_msg = DriveMessage()
        self.check_msg = CheckMessage()
        self.transmitter = Transmitter(interface='socketcan', channel='can0')

        self.lock = Lock()

    def locked(self, fun):
        try:
            self.lock.acquire()
            fun()
        finally:
            self.lock.release()

    @locked
    def periodic_update(self):
        try:
            self.lock.acquire()
            self.drive_msg.increment_msg_count()
            self.check_msg.increment_msg_count()
            self.send_messages()
        finally:
            self.lock.release()

    def send_messages(self):
        if self.drive_msg is not None:
            self.transmitter.transmit(self.drive_msg)
        if self.check_msg is not None:
            self.transmitter.transmit(self.check_msg)

    @locked
    def set_velocity(self, velocity: Union[int, float]) -> None:
        self.drive_msg.velocity = Driving.to_can(int(velocity))
        self.send_messages()

    @locked
    def set_acceleration(self, acceleration: int) -> None:
        self.drive_msg.acceleration_level = acceleration
        self.send_messages()

    @locked
    def set_steering(self, steering: Union[int, float]) -> None:
        self.drive_msg.steering = Steering.to_can(int(steering))
        self.send_messages()

    @locked
    def set_steering_precision(self, precision: int) -> None:
        self.drive_msg.steering_level = precision
        self.send_messages()

    @locked
    def release_control(self) -> None:
        self.drive_msg.ctrl = 0
        self.send_messages()
