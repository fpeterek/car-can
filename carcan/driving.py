from typing import Union


class Driving:
    zero = 0
    max_backwards = -30 / 3.6  # m/s
    max_forward = 30 / 3.6  # m/s
    error_tolerance = max_forward / 10

    can_max = 127
    can_min = -127

    ratio = 127 / max_forward

    @staticmethod
    def trunc_value(value: Union[int, float]) -> float:
        return max(min(Driving.max_forward, value), Driving.max_backwards)

    @staticmethod
    def trunc_can(value: Union[int, float]) -> int:
        value = int(value)  # Ensure value is int
        return max(min(Driving.can_max, value), Driving.can_min)

    @staticmethod
    def to_can(value: Union[int, float]) -> int:
        value *= Driving.ratio
        trunced = Driving.trunc_can(value)
        return trunced if trunced >= 0 else 255+trunced

    @staticmethod
    def to_value(value: Union[int, float]) -> float:
        value = value if value <= 127 else value-255
        value /= Driving.ratio
        return Driving.trunc_value(value)
