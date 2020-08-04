from carcan.carcan import CanInterface
from carcan.steering import Steering

import time

from driving import Driving


def steer_left(car: CanInterface) -> None:
    car.steer(Steering.max_left)
    while car.steering_angle > Steering.max_left:
        time.sleep(0.05)


def steer_right(car: CanInterface) -> None:
    car.steer(Steering.max_right)
    while car.steering_angle < Steering.max_right:
        time.sleep(0.05)


def revert(car: CanInterface) -> None:
    car.forward()
    while car.steering_angle < Steering.neutral:
        time.sleep(0.05)


def steering_test(car: CanInterface):
    for i in range(0, 3):
        steer_left(car)
        steer_right(car)
    revert(car)


def forward(car: CanInterface) -> None:
    car.move(Driving.max_forward)
    while car.velocity != Driving.max_forward:
        time.sleep(0.05)


def backwards(car: CanInterface) -> None:
    car.move(Driving.max_backwards)
    while car.velocity != Driving.max_backwards:
        time.sleep(0.05)


def stop(car: CanInterface) -> None:
    car.stop()
    while car.velocity != Driving.zero:
        time.sleep(0.05)


def driving_test(car: CanInterface):
    for i in range(0, 3):
        forward(car)
        backwards(car)
    stop(car)


def car_test():
    car = CanInterface()
    steering_test(car)
    driving_test(car)
    car.shutdown()

