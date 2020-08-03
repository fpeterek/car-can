from typing import Union


class Driving:
    neutral = 0
    max_backwards = -50
    max_forward = 50

    can_offset = 127
    can_min = 0
    can_max = 254

    ratio = (can_max - can_offset) / max_forward

    @staticmethod
    def trunc_value(value: Union[int, float]) -> int:
        value = int(value)  # Ensure value is int
        return max(min(Driving.max_forward, value), Driving.max_backwards)

    @staticmethod
    def trunc_can(value: Union[int, float]) -> int:
        value = int(value)  # Ensure value is int
        return max(min(Driving.can_max, value), Driving.can_min)

    @staticmethod
    def to_can(value: Union[int, float]) -> int:
        value *= Driving.ratio
        value += Driving.neutral
        return Driving.trunc_can(value)

    @staticmethod
    def to_value(value: Union[int, float]) -> int:
        value -= Driving.can_offset
        value /= Driving.ratio
        return Driving.trunc_value(value)
