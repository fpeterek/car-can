import time

from driving import Driving
from steering import Steering
from car import Car


def steer_right(car: Car) -> None:
    car.set_steering(Steering.max_left)
    while car.steering_angle - 4 > Steering.max_left:
        print('Car steer angle:', car.steering_angle)
        time.sleep(0.01)


def steer_left(car: Car) -> None:
    car.set_steering(Steering.max_right)
    while car.steering_angle + 4 < Steering.max_right:
        print('Car steer angle:', car.steering_angle)
        time.sleep(0.01)


def revert(car: Car) -> None:
    car.set_steering(Steering.neutral)
    while car.steering_angle - 1 < Steering.neutral < car.steering_angle + 1:
        time.sleep(0.01)


def steering_test(car: Car):
    for i in range(0, 3):
        steer_left(car)
        time.sleep(1)
        steer_right(car)
        time.sleep(1)
    revert(car)


def forward(car: Car) -> None:
    car.set_velocity(Driving.max_forward / 2)
    while car.velocity < (Driving.max_forward / 2) * 0.9:
        time.sleep(0.05)


def backwards(car: Car) -> None:
    car.set_velocity(Driving.max_backwards / 2)
    while car.velocity > (Driving.max_backwards / 2) * 0.9:
        time.sleep(0.05)


def stop(car: Car) -> None:
    car.set_velocity(0)
    while car.velocity != Driving.zero:
        time.sleep(0.05)


def driving_test(car: Car):
    for i in range(0, 3):
        forward(car)
        backwards(car)
    stop(car)


def car_test():
    print("Running test...")
    car = Car()
    steering_test(car)
    driving_test(car)
    car.shutdown()
    print("Test done...")

