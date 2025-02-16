from typing import Optional

import can

from tx_message import TxMessage, DriveMessage, CheckMessage


class Transmitter:
    def __init__(self, bus: can.interface.Bus):
        self.drive: Optional[can.ModifiableCyclicTaskABC] = None
        self.check: Optional[can.ModifiableCyclicTaskABC] = None
        self._bus = bus

    def _create_periodic(self, msg: TxMessage) -> can.ModifiableCyclicTaskABC:
        return self._bus.send_periodic(msg=msg.can_message, period=msg.period)

    def transmit_drive_msg(self, msg: DriveMessage) -> None:
        if self.drive is None:
            self.drive = self._create_periodic(msg)
        else:
            self.drive.modify_data(msg.can_message)

    def transmit_check_message(self, msg: CheckMessage):
        if self.check is None:
            self.check = self._create_periodic(msg)
        else:
            self.check.modify_data(msg.can_message)

    def transmit(self, msg: TxMessage) -> None:
        if isinstance(msg, DriveMessage):
            self.transmit_drive_msg(msg)
        elif isinstance(msg, CheckMessage):
            self.transmit_check_message(msg)
        else:
            raise ValueError(f'Unsupported message type {type(msg)}')

    def shutdown(self) -> None:
        self.drive.stop()
        self.check.stop()
