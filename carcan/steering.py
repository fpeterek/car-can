from typing import Union


class Steering:
    neutral = 0
    max_left = -20
    max_right = 20
    error_tolerance = 2

    can_offset = 127
    can_min = 0
    can_max = 254

    ratio = (can_max - can_offset) / max_right

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
        value *= -1  # Values are flipped -> 0 means left, 254 means right
        value *= Steering.ratio
        value += Steering.can_offset
        return Steering.trunc_can(value)

    @staticmethod
    def to_value(value: Union[int, float]) -> int:
        value -= Steering.can_offset
        value /= Steering.ratio
        value *= -1  # Values are flipped -> 0 means left, 254 means right
        return Steering.trunc_value(value)

