class ID:
    class Cmd:
        def __init__(self):
            self.check = 8
            self.drive = 201

    class Feedback:
        def __init__(self):
            self.check = 5
            self.info1 = 202
            self.info2 = 203

    command: Cmd = Cmd()
    feedback: Feedback = Feedback()
