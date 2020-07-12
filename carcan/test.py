from carcan.carcan import CanInterface
from carcan.steering import Steering

import time

from driving import Driving


def steer_left(car: CanInterface) -> None:
    car.steer(Steering.left_max)
    while car.steering_angle > Steering.left_max:
        time.sleep(0.02)


def steer_right(car: CanInterface) -> None:
    car.steer(Steering.right_max)
    while car.steering_angle < Steering.right_max:
        time.sleep(0.02)


def steering_test():
    car = CanInterface()
    for i in range(0, 5):
        steer_left(car)
        steer_right(car)
    car.stop()


def forward(car: CanInterface) -> None:
    car.move(Driving.max_forward)
    while car.velocity != Driving.max_forward:
        time.sleep(0.02)


def backwards(car: CanInterface) -> None:
    car.move(Driving.max_backwards)
    while car.velocity != Driving.max_backwards:
        time.sleep(0.02)


def driving_test():
    car = CanInterface()
    for i in range(0, 5):
        forward(car)
        backwards(car)
    car.stop()

