import socket
from threading import Lock, Thread

from request import Request
from response import Response

class Server:
    BUFFERSIZE = 1024
    def __init__(self, host: str, port: int, debug:bool=False):
        self._host = host
        self._port = port
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._debug = debug
        self._print_lock = Lock()

    def initialize(self):
        self._s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._s.bind((self._host, self._port))
        self._s.listen(5) # Don't know what the number does and seems to not matter
        self._debug_print(f"listening on {self._host}:{self._port}")
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            try:
                conn, addr = self._s.accept()
                self._debug_print(f"Accepted connection from {str(addr)}")
                t = Thread(target=self.handle_client, args=(conn, addr))
                t.start()
            except KeyboardInterrupt:
                self._running = False

        self._debug_print("Closing server")
        self._s.close()

    def handle_client(self, conn: socket.socket, addr):
        data = conn.recv(Server.BUFFERSIZE)
        req = Request()
        if req.parse(data):
            self._debug_print(f"Incoming {req.get_method().value} request for {req._path} from {str(addr)}")
            resp = Response()
            resp.compose_response(req)
            to_send = resp.encode()
            conn.send(to_send)

        self._debug_print(f"Closing connection from {str(addr)}")
        conn.close()

    def _debug_print(self, msg):
        if self._debug:
            with self._print_lock:
                print(msg)
