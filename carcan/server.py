import socketserver
import os

from carinterface import CarInterface


debug = os.getenv('SOCKET_DEBUG') and os.getenv('SOCKET_DEBUG').lower() in ('true', '1')


class Server:

    _car: CarInterface = None

    class Handler(socketserver.BaseRequestHandler):

        def drive(self, v, s):
            if debug:
                print(f'Received (v, s) = ({v}, {s})')

            if Server._car is not None:
                Server._car.drive(v, s)

            self.healthcheck()

        def healthcheck(self):
            if debug:
                status = Server._car.is_ok if Server._car is not None else False
                print(f'Healthcheck (status={("Dead", "Alive")[status]})')

            status = int(Server._car.is_ok if Server._car is not None else False)
            self.request.sendall(status.to_bytes(1, 'little'))

        def info(self):

            v = Server._car.velocity if Server._car is not None else 0
            s = Server._car.steering_angle if Server._car is not None else 0
            b = int(Server._car.ebrake_enabled if Server._car is not None else False)
            if debug:
                print(f'Driving data (v, s) = ({v}, {s})')

            v = v.to_bytes(1, 'little', signed=True)
            s = s.to_bytes(1, 'little', signed=True)
            b = b.to_bytes(1, 'little', signed=True)
            self.request.sendall(v + s + b)

        def ebrake(self, brake: bool):
            if debug:
                print(f'Emergency brake {["released", "engaged"][int(brake)]}')

            if Server._car is not None:
                Server._car.set_ebrake(brake)

            self.healthcheck()

        def position(self):
            ok = 0
            try:
                x, y = 0, 0 if Server._car is None else Server._car.gps_position
                ok = int(Server._car is not None)
            except:
                x, y = 0, 0
            x = int(x * 10000000)
            y = int(x * 10000000)
            ok = ok.to_bytes(1, 'little', signed=False)
            x = x.to_bytes(8, 'little', signed=True)
            y = y.to_bytes(8, 'little', signed=True)

            self.request.sendall(ok + x + y)

        def handle(self):
            data = self.request.recv(3)
            message_type = int.from_bytes(data[0:1], 'little', signed=False)
            b1 = int.from_bytes(data[1:2], 'little', signed=True)
            b2 = int.from_bytes(data[2:3], 'little', signed=True)

            if message_type == 0:
                self.drive(v=b1, s=b2)
            elif message_type == 1:
                self.healthcheck()
            elif message_type == 2:
                self.info()
            elif message_type == 3:
                self.ebrake(brake=bool(b1))
            elif message_type == 4:
                self.position()

    @staticmethod
    def serve(car: CarInterface = None, host: str = None, port: int = None):

        Server._car = car if car is not None else CarInterface(interface="socketcan", channel="can0")

        if not host:
            host = os.getenv("SERVER_HOST")
        if port is None or port < 0:
            port = int(os.getenv("SERVER_PORT"))

        try:
            with socketserver.TCPServer((host, port), Server.Handler) as server:
                print('Starting server...')
                server.serve_forever()
        finally:
            if Server._car is not None:
                Server._car.shutdown()
