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

            if debug:
                print(f'Driving data (v, s) = ({v}, {s})')

            v = v.to_bytes(1, 'little', signed=True)
            s = s.to_bytes(1, 'little', signed=True)
            self.request.sendall(v + s)

        def handle(self):
            data = self.request.recv(3)
            t = int.from_bytes(data[0:1], 'little', signed=False)
            v = int.from_bytes(data[1:2], 'little', signed=True)
            s = int.from_bytes(data[2:3], 'little', signed=True)

            if t == 0:
                self.drive(v, s)
            elif t == 1:
                self.healthcheck()
            elif t == 2:
                self.info()

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
