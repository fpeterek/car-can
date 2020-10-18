from typing import Union


class Driving:
    zero = 0
    max_backwards = -30 / 3.6  # m/s
    max_forward = 30 / 3.6  # m/s
    error_tolerance = max_forward / 10

    can_offset = 127
    can_min = 0
    can_max = 254

    ratio = (can_max - can_offset) / max_forward

    @staticmethod
    def trunc_value(value: Union[int, float]) -> float:
        return max(min(Driving.max_forward, value), Driving.max_backwards)

    @staticmethod
    def trunc_can(value: Union[int, float]) -> int:
        value = int(value)  # Ensure value is int
        return max(min(Driving.can_max, value), Driving.can_min)

    @staticmethod
    def to_can(value: Union[int, float]) -> int:
        value *= -1  # Values are flipped -> 0 means forward, 254 means backwards
        value *= Driving.ratio
        value += Driving.can_offset
        return Driving.trunc_can(value)

    @staticmethod
    def to_value(value: Union[int, float]) -> float:
        value -= Driving.can_offset
        value /= Driving.ratio
        value *= -1  # Values are flipped -> 0 means forward, 254 means backwards
        return Driving.trunc_value(value)
