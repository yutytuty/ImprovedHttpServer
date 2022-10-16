import socket

from server import Server

server = Server("localhost", 8888, debug=True)
server.initialize()
server.run()
