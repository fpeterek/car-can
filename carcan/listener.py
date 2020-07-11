import can

from carcan.id import ID


class CanListener(can.listener.Listener):

    def __init__(self):
        self.funs = {
            ID.feedback.speed: self.decode_velocity,
            ID.feedback.steer: self.decode_steer
        }

    @staticmethod
    def decode(b1: int, b2: int) -> int:
        return (b1 << 0) + (b2 << 8)

    def decode_velocity(self, msg: can.Message) -> int:
        pass

    def decode_steer(self, msg: can.Message) -> None:
        b1 = msg.data[0]
        b2 = msg.data[1]
        decoded = CanListener.decode(b1, b2)

    def on_message_received(self, msg: can.Message):
        if msg.arbitration_id not in self.funs:
            return
        fun = self.funs[msg.arbitration_id]
        fun(msg)
