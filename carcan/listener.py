import can

from carcan.id import ID


class CanListener(can.listener.Listener):

    def __init__(self, steer_setter, velocity_setter):
        self.funs = {
            ID.feedback.speed: self.decode_velocity,
            ID.feedback.steer: self.decode_steer
        }

        self.set_steer = steer_setter
        self.set_velocity = velocity_setter

    @staticmethod
    def decode(b1: int, b2: int) -> int:
        return (b1 << 0) + (b2 << 8)

    def decode_velocity(self, msg: can.Message) -> None:
        b1 = msg.data[6]
        b2 = msg.data[5]
        self.set_velocity(CanListener.decode(b1, b2))

    def decode_steer(self, msg: can.Message) -> None:
        b1 = msg.data[0]
        b2 = msg.data[1]
        self.set_steer(CanListener.decode(b1, b2))

    def on_message_received(self, msg: can.Message):
        if msg.arbitration_id not in self.funs:
            return
        fun = self.funs[msg.arbitration_id]
        fun(msg)
