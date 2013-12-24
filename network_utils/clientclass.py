import protocol_pb2 as proto
from twisted.internet.protocol import DatagramProtocol


class Client(DatagramProtocol):
    """docstring for Client"""
    def __init__(self):
        self.time = 0
        self.input = proto.input()
        self.connected = False
        self.host = ('127.0.0.1', 8000)
        self.con_timer = 0
        self.server_data = proto.Player()
        self.id = None

    def start_connection(self):
        self.transport.connect(*self.host)
        self.input.type = proto.newplayer
        self.input.name = 'asdf'
        self.input.time = 0
        self.transport.write(self.input.SerializeToString())

    def get_input(self, event, msg):
        self.input, dt = msg
        if self.connected:
            self.time += int(dt * 10000)
            self.input.time = self.time
            self.input.type = proto.update
            self.transport.write(self.input.SerializeToString(), self.host)

    def datagramReceived(self, datagram, address):
        self.server_data.ParseFromString(datagram)
        print self.server_data
