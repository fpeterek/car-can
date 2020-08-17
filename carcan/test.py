from carinterface import CanInterface
from steering import Steering

import time

from driving import Driving


def steer_right(car: CanInterface) -> None:
    car.steer(Steering.max_left)
    while car.steering_angle - 4 > Steering.max_left:
        print('Car steer angle:', car.steering_angle, 'desired angle:', car._desired_steering_angle)
        time.sleep(0.01)


def steer_left(car: CanInterface) -> None:
    car.steer(Steering.max_right)
    while car.steering_angle + 4 < Steering.max_right:
        print('Car steer angle:', car.steering_angle, 'desired angle:', car._desired_steering_angle)
        time.sleep(0.01)


def revert(car: CanInterface) -> None:
    car.forward()
    while car.steering_angle < Steering.neutral:
        time.sleep(0.01)


def steering_test(car: CanInterface):
    for i in range(0, 3):
        steer_left(car)
        time.sleep(1)
        steer_right(car)
        time.sleep(1)
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
    print("Running test...")
    car = CanInterface(interface="socketcan", channel="can0")
    car.move(Driving.max_backwards)
    print(car._desired_velocity)
    time.sleep(5)
    car.stop()
    # steering_test(car)
    # driving_test(car)
    car.shutdown()
    print("Test done...")

