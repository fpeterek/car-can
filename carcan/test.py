from carcan.carcan import CanInterface
from carcan.steering import Steering

import time


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


def driving_test():
    print('Test')

