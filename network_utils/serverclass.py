from twisted.internet.protocol import DatagramProtocol
import protocol_pb2 as proto
from maps.map import Map
from player.player import player


class GameServer(DatagramProtocol):
    """docstring for GameServer"""
    def __init__(self):
        # super(GameServer, self).__init__()
        self.players = {}
        self.players_pack = {}
        self.timers = {}
        self.map = Map('testmap')

    def datagramReceived(self, datagram, address):
        data = proto.input()
        data.ParseFromString(datagram)
        if data.type == proto.newplayer:
            pl_id = self.get_id()
            self.players[pl_id] = player()
            self.players[pl_id].address = address
            self.players[pl_id].name = data.name
            print 'new player ' + data.name
            self.players[pl_id].time = 0
            self.players[pl_id].spawn(100, 300)
            self.players_pack[pl_id] = proto.Player()
            self.player_to_pack(pl_id)
            self.timers[pl_id] = 0
            spam = proto.Player()
            spam.type = proto.mapupdate
            spam.id = pl_id
            self.transport.write(spam.SerializeToString(), address)
        if data.type == proto.update:
            self.get_input(data)
            dt = data.time - self.players[data.id].time
            if dt > 0:
                dt = dt / 10000.
            # update movement
                self.players[data.id].update(dt)
                self.collide(data.id)
                self.player_to_pack(data.id)
                self.players[data.id].time = data.time
                self.timers[data.id] = 0

    def update(self, dt):
        keys = []
        for key in self.timers:
            self.timers[key] += dt
            if self.timers[key] > 10:
                keys.append(key)
        for key in keys:
            print self.players[key].name + 'deleted'
            del self.players[key], self.players_pack[key], self.timers[key]
        self.send_all()

    def send_all(self):
        for idx, player in self.players.iteritems():
            for idx_, pack in self.players_pack.iteritems():
                self.transport.write(pack.SerializeToString(), player.address)

    def get_id(self):
        idx = 0
        while idx in self.players:
            idx += 1
        return idx

    def player_to_pack(self, idx):
        self.players_pack[idx].posx = self.players[idx].pos[0]
        self.players_pack[idx].posy = self.players[idx].pos[1]

        self.players_pack[idx].velx = self.players[idx].vel[0]
        self.players_pack[idx].vely = self.players[idx].vel[1]

        self.players_pack[idx].type = proto.update

    def get_input(self, data):
        self.players[data.id].Move.input.up = data.up
        self.players[data.id].Move.input.right = data.right
        self.players[data.id].Move.input.left = data.left

    def collide(self, idx):
        for rect in self.map.quad_tree.retrieve([], self.players[idx].Rect):
            coll = self.players[idx].Rect.collides(rect)
            if coll:
                ovr, axis = coll
                self.players[idx].resolve_collision(ovr, axis, rect.angle)

        for keys in self.players:
            if keys != idx:
                coll = self.players[idx].Rect.collides(self.players[keys].Rect)
                if coll:
                    ovr, axis = coll
                    self.players[idx].resolve_collision(ovr, axis, 0)
