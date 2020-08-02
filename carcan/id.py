class ID:
    class Cmd:
        def __init__(self):
            self.check = 8
            self.status = 201
            self.drive = 202

    class Feedback:
        def __init__(self):
            self.check = 5
            self.info = 203

    command: Cmd = Cmd()
    feedback: Feedback = Feedback()
