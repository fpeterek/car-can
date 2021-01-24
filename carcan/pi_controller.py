import math
import time


class Controller:
    def __init__(self, gain: float):
        self.target = 0.0
        self.gain = gain


class Integrator(Controller):
    def __init__(self, gain: float):
        super(Integrator, self).__init__(gain)
        self.sum = 0

    def update(self, error) -> float:
        self.sum += error
        return self.sum * self.gain


class Linear(Controller):
    def __init__(self, gain: float):
        super(Linear, self).__init__(gain)

    def update(self, error) -> float:
        return error * self.gain


class PIController:
    def __init__(self, proportional: float, integral: float):
        self._target = 0
        self.current = 0
        self.output = 0

        self.linear = Linear(proportional)
        self.integral = Integrator(integral)

    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, target: float) -> None:
        self._target = target
        self.linear.target = target
        self.integral.target = target

    def update(self, current: float) -> float:
        self.current = current
        error = self.target - current
        linear = self.linear.update(error)
        integral = self.integral.update(error)
        self.output = linear + integral
        return self.output


def test():
    controller = PIController(proportional=0.1, integral=0.1)

    controller.target = 60

    while not math.isnan(controller.output) and controller.output != controller.target:
        controller.update(controller.output)
        time.sleep(0.1)
        print(f'Current output: {controller.output}')


if __name__ == '__main__':
    test()
