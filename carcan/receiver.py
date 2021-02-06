from typing import Callable, List

import can

from car_data import CarData
import crc
from steering import Steering
from driving import Driving


class Receiver(can.listener.Listener):

    def __init__(self, bus: can.interface.Bus, on_update: Callable[[CarData], None],
                 on_can_error: Callable[[], None]):

        self._bus = bus
        self.car_data = CarData()
        self.on_update = on_update
        self.on_can_error = on_can_error

        self.handlers = {
            5: self.check,
            202: self.data1,
            203: self.data2,
        }

    def handler(self, fun):
        def update_fun(msg: can.Message):
            if not Receiver.check_integrity(msg.data):
                return
            fun(msg)
            self.on_update(self.car_data)

        return update_fun

    @staticmethod
    def check_integrity(data: List[int]):
        return data[-1] == crc.calc_crc(data[0:-1])

    def check(self, msg: can.Message):
        if not Receiver.check_integrity(msg.data):
            return
        self.car_data.rx_check = msg.data[0]
        self.on_update(self.car_data)

    def data1(self, msg: can.Message):
        if not Receiver.check_integrity(msg.data):
            return self.on_can_error()
        data = msg.data

        self.car_data.steering_angle = Steering.to_value(data[0])
        self.car_data.wheel_data.fr.rpm = data[1]
        self.car_data.wheel_data.fl.rpm = data[2]
        self.car_data.wheel_data.rr.rpm = data[3]
        self.car_data.wheel_data.rl.rpm = data[4]
        self.car_data.velocity = Driving.to_value(data[5])
        self.on_update(self.car_data)

    def data2(self, msg: can.Message):
        if not Receiver.check_integrity(msg.data):
            return self.on_can_error()
        data = msg.data

        self.car_data.has_control = bool(data[0])
        self.car_data.acceleration_level = data[1]
        self.car_data.steering_level = data[2]
        self.car_data.max_torque = data[3]
        self.car_data.max_steering_speed = data[4]

        self.on_update(self.car_data)

    def on_message_received(self, msg: can.Message):
        fn = self.handlers.get(msg.arbitration_id)
        if fn is not None:
            fn(msg)
