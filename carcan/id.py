class ID:
    class Cmd:
        def __init__(self):
            self.drive = 0x64

    class Feedback:
        def __init__(self):
            self.steer = 0x30C
            self.speed = 0x96

    command: Cmd = Cmd()
    feedback: Feedback = Feedback()
