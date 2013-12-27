import protocol_pb2 as proto
from twisted.internet.protocol import DatagramProtocol
import time


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

        self.listeners = {}

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
        if self.server_data.type == proto.mapupdate:
            self.connected = True
            self.input.id = self.server_data.id
            print 'connected'
        self.send_message('serverdata', self.server_data)

    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg=None):
        for listener, events in self.listeners.items():
            try:
                listener(event, msg)
            except (Exception, ):
                self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]
