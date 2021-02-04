from typing import Union


class Steering:
    neutral = 0
    max_left = -20
    max_right = 20
    error_tolerance = 2

    can_min = -127
    can_max = 127

    ratio = 127 / max_right

    @staticmethod
    def trunc_value(value: Union[int, float]) -> int:
        value = int(value)  # Ensure value is int
        return max(min(Steering.max_right, value), Steering.max_left)

    @staticmethod
    def trunc_can(value: Union[int, float]) -> int:
        value = int(value)  # Ensure value is int
        return max(min(Steering.can_max, value), Steering.can_min)

    @staticmethod
    def to_can(value: Union[int, float]) -> int:
        value *= Steering.ratio
        trunced = Steering.trunc_can(value)
        return trunced if trunced >= 0 else 255+trunced

    @staticmethod
    def to_value(value: Union[int, float]) -> int:
        value = value if value <= 127 else value-255
        value /= Steering.ratio
        return Steering.trunc_value(value)

