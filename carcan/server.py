import socketserver
import os

from carinterface import CarInterface


class Server:

    _car: CarInterface = None

    class Handler(socketserver.BaseRequestHandler):

        def handle(self):
            data = self.request.recv(2)
            v = int.from_bytes(data[0:1], 'little', signed=True)
            s = int.from_bytes(data[1:2], 'little', signed=True)

            print(f'Received (v, s) = ({v}, {s})')

            if Server._car is not None:
                Server._car.drive(v, s)

            self.request.sendall((1).to_bytes(1, 'little'))

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
