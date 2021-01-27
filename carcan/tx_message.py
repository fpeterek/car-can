from typing import List

import can

import crc
from id import ID


class TxMessage:
    def __init__(self, msg_id: int, period: float):
        self.msg_id = msg_id
        self.period = period
        self.msg_count = 0

    @staticmethod
    def checksum(data: List[int]) -> int:
        return crc.calc_crc(data)

    def _form_message(self, data: List[int]) -> can.Message:
        return can.Message(arbitration_id=self.msg_id, data=data, is_extended_id=False)

    def increment_msg_count(self):
        self.msg_count = (self.msg_count + 1) % 256

    @property
    def can_message(self):
        data = self.data + [TxMessage.checksum(self.data)]
        return self._form_message(data)

    @property
    def data(self) -> List[int]:
        return [0, 0, 0, 0, 0, 0, 0]


class DriveMessage(TxMessage):
    def __init__(self):
        super(DriveMessage, self).__init__(msg_id=ID.command.drive, period=0.02)

        self.status = 1
        self.ctrl = 1
        self.velocity = 0
        self.acceleration_level = 0
        self.steering = 0
        self.steering_level = 0

    @property
    def data(self) -> List[int]:
        return [
            self.status, self.ctrl, self.steering, self.velocity, self.acceleration_level, self.steering_level,
            self.msg_count
        ]


class CheckMessage(TxMessage):
    def __init__(self):
        super(CheckMessage, self).__init__(msg_id=ID.command.check, period=0.02)

        self.stop = 0
        self.tx_check = 0
        self.fault_count = 0
        self.fault_codes = 0
        self.reserved1 = 0
        self.reserved2 = 0

    @property
    def data(self) -> List[int]:
        return [
            self.stop, self.tx_check, self.fault_count, self.fault_codes, self.reserved1, self.reserved2, self.msg_count
        ]
