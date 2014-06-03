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

        self.listeners = {}

    def start_connection(self):
        # self.transport.connect(*self.host)
        self.input.type = proto.newplayer
        self.input.name = 'asdf'
        self.input.time = 0
        self.transport.write(self.input.SerializeToString(), self.host)

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
            self.id = self.server_data.id
            print 'connected'
        if self.server_data.type == proto.update:
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


class move(object):
    """docstring for move"""
    def __init__(self, time, input, state):
        super(move, self).__init__()
        self.time = time
        self.input = input
        self.state = state


class moves(object):
    """docstring for moves"""
    def __init__(self, maximum):
        super(moves, self).__init__()
        self.maximum = maximum
        self.moves = []

    def advance(self, index):
        index[0] += 1
        if index[0] >= self.maximum:
            index[0] -= self.maximum


def correct_client(update_physics, state):
    """update_physics is a function which updates physics and has dt, state
    as an argument. state is the state sent from server as in
    player.state.state"""
    pass
