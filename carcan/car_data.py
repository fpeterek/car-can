
class CarData:
    def __init__(self):
        self.rx_check = 0
        self.reserved0 = 0
        self.reserved1 = 0
        self.reserved2 = 0
        self.reserved3 = 0
        self.reserved4 = 0

        self.steering_angle = 0
        self.wheel_data = WheelData()
        self.velocity = 0

        self.has_control = False
        self.acceleration_level = 0
        self.steering_level = 0
        self.max_torque = 0
        self.max_steering_speed = 0
        self.reserved5 = 0


class WheelData:
    def __init__(self):
        self.fr = Wheel()
        self.fl = Wheel()
        self.rr = Wheel()
        self.rl = Wheel()


class Wheel:
    def __init__(self):
        self.rpm = 0
