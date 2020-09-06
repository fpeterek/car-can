import can

from id import ID


class CanListener(can.listener.Listener):

    def __init__(self, check_setter, driving_info_setter):
        self.funs = {
            ID.feedback.check: self.decode_check,
            ID.feedback.info: self.decode_drive_data,
        }

        self.set_check = check_setter
        self.set_driving_info = driving_info_setter

    def decode_check(self, msg: can.Message):
        value = msg.data[1]
        self.set_check(value)

    def decode_drive_data(self, msg: can.Message):
        steer = msg.data[0]
        speed = msg.data[1]
        ctrl = bool(msg.data[2])
        self.set_driving_info(steer, speed, ctrl)

    def on_message_received(self, msg: can.Message):
        if msg.arbitration_id not in self.funs:
            return
        fun = self.funs[msg.arbitration_id]
        fun(msg)
