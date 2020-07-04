import os

import can


class CanInterface:
    def __init__(self, interface=None, channel=None, bitrate=None):
        default_conf = can.util.load_config()
        bustype = interface if interface else default_conf['interface']
        channel = channel if channel else default_conf['channel']
        bitrate = bitrate if bitrate is not None else default_conf['bitrate']

        listeners = []
        if os.getenv('CAN_DEBUG'):
            listeners.append(can.Printer())

        self.bus = can.interface.Bus(bustype=bustype, channel=channel, bitrate=bitrate)
        self.notifier = can.Notifier(self.bus, listeners)

    def steer(self, degree: float):
        pass
