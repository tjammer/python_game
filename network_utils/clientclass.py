import protocol_pb2 as proto
from twisted.internet.protocol import DatagramProtocol
from player.state import state, vec2


class Client(DatagramProtocol):
    """docstring for Client"""
    def __init__(self):
        self.time = 0
        self.connected = False
        #self.host = ('pipc73.pit.physik.uni-tuebingen.de', 8000)
        self.host = ('127.0.0.1', 8000)
        self.con_timer = 0
        self.message = proto.Message()
        self.input = proto.Input()
        self.id = None

        self.listeners = {}

    def start_connection(self):
        # self.transport.connect(*self.host)
        self.message.Clear()
        self.message.type = proto.newPlayer
        self.message.input.Clear()
        self.message.input.name = 'asdf'
        self.message.input.time = 0
        self.transport.write(self.message.SerializeToString(), self.host)

    def disconnect(self):
        if self.connected:
            self.message.Clear()
            self.input.Clear()
            self.message.type = proto.disconnect
            self.input.id = self.id
            self.input.time = 0
            self.message.input.CopyFrom(self.input)
            self.transport.write(self.message.SerializeToString(), self.host)
        self.connected = False
        self.id = None

    def get_input(self, event, msg):
        #self.input, dt = msg
        self.input, self.time = msg
        if self.connected:
            self.message.Clear()
            self.message.type = proto.playerUpdate
            self.input.time = self.time
            self.input.id = self.id
            self.message.input.CopyFrom(self.input)
            self.transport.write(self.message.SerializeToString(), self.host)

    def datagramReceived(self, datagram, address):
        self.message.ParseFromString(datagram)
        if self.message.type == proto.mapUpdate and not self.id:
            self.connected = True
            self.id = self.message.player.id
            self.send_message('on_connect', self.id)
        elif self.message.type == proto.playerUpdate and self.connected:
            ind = self.message.player.id
            state = self.server_to_state(self.message.player)
            time = self.message.player.time
            self.send_message('serverdata',
                              (proto.playerUpdate, (ind, time, state)))
        elif self.message.type == proto.newPlayer and self.connected:
            ind = self.message.player.id
            state = self.server_to_state(self.message.player)
            time = self.message.player.time
            self.send_message('serverdata',
                              (proto.newPlayer, (ind, time, state)))
        elif self.message.type == proto.disconnect and self.connected:
            ind = self.message.player.id
            self.send_message('serverdata', (proto.disconnect, ind))

    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg=None):
        for listener, events in self.listeners.items():
          #  try:
            listener(event, msg)
        #    except (Exception, ):
         #       self.unregister(listener, msg)

    def unregister(self, listener, msg):
        print '%s deleted, %s' % (listener, msg)
        del self.listeners[listener]

    def server_to_state(self, data):
        pos = vec2(data.posx, data.posy)
        vel = vec2(data.velx, data. vely)
        hp = data.hp
        return state(pos, vel, hp)


class move(object):
    """docstring for move"""
    def __init__(self, time, input, state):
        super(move, self).__init__()
        self.time = time
        self.input = input
        self.state = state


class moves(list):
    """docstring for moves"""
    def __init__(self, maximum):
        super(moves, self).__init__()
        self.maximum = maximum

    def advance(self, index):
        index[0] += 1
        if index[0] >= self.maximum:
            index[0] -= self.maximum


def correct_client(update_physics, s_move, moves, head, tail):
    """update_physics is a function which updates physics and has dt, state
    and input as an argument. state is the state sent from server as in
    player.state.state"""
    threshold = 5

    while s_move.time > moves[head[0]].time and head[0] != tail:
        moves.advance(head)

    if head[0] != tail and s_move.time == moves[head[0]].time:
        if (moves[head[0]].state.pos - s_move.state.pos).mag() > threshold:
            c_time = s_move.time
            c_state = s_move.state.copy()
            c_input = moves[head[0]].input

            moves.advance(head)
            index = [head[0]]
            while index[0] != tail:
                dt = (moves[index[0]].time - c_time) / 10000.
                c_state = update_physics(dt, c_state, c_input)

                c_time = moves[index[0]].time
                c_input = moves[index[0]].input
                moves[index[0]].state = c_state.copy()
                moves.advance(index)
