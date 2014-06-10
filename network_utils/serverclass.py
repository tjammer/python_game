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
        self.map = Map('testmap', server=True)

    def datagramReceived(self, datagram, address):
        data = proto.input()
        data.ParseFromString(datagram)
        if data.type == proto.newplayer:
            pl_id = self.get_id()
            self.init_player(data, address, pl_id)
        if data.type == proto.update and data.id == self.find_id(address):
            self.get_input(data)
            dt = data.time - self.players[data.id].time
            if dt > 0:
                dt = dt / 10000.
                # update movement
                self.players[data.id].update(dt)
                self.collide(data.id)
                self.players[data.id].time = data.time
                self.player_to_pack(data.id)
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
        for idx, player_ in self.players.iteritems():
            for idx_, pack in self.players_pack.iteritems():
                self.transport.write(pack.SerializeToString(), player_.address)

    #find next available id
    def get_id(self):
        idx = 1
        while idx in self.players:
            idx += 1
        return idx

    #find id of adress
    def find_id(self, address):
        for idx in self.players:
            if address == self.players[idx].address:
                return idx
        return -1

    def player_to_pack(self, idx):
        self.players_pack[idx].posx = self.players[idx].state.pos.x
        self.players_pack[idx].posy = self.players[idx].state.pos.y
        self.players_pack[idx].velx = self.players[idx].state.vel.x
        self.players_pack[idx].vely = self.players[idx].state.vel.y
        self.players_pack[idx].hp = self.players[idx].state.hp
        self.players_pack[idx].time = self.players[idx].time

        self.players_pack[idx].type = proto.update

    def get_input(self, data):
        self.players[data.id].input.up = data.up
        self.players[data.id].input.right = data.right
        self.players[data.id].input.left = data.left

    def collide(self, idx):
        for keys in self.players:
            if keys != idx:
                coll = self.players[idx].Rect.collides(self.players[keys].Rect)
                if coll:
                    ovr, axis = coll
                    self.players[idx].resolve_collision(ovr, axis, 0)
        #collide with players first to not get collided into wall
        for rect in self.map.quad_tree.retrieve([], self.players[idx].Rect):
            coll = self.players[idx].Rect.collides(rect)
            if coll:
                ovr, axis = coll
                self.players[idx].resolve_collision(ovr, axis, rect.angle)

    def init_player(self, data, address, pl_id):
        #check if name already exists
        name = data.name
        i = 1
        while name in [p.name for p in self.players.itervalues()]:
            name = data.name + '_' + str(i)
            i += 1
        self.players[pl_id] = player(server=True)
        self.players[pl_id].address = address
        self.players[pl_id].name = name
        print ' '.join((name, 'joined the server.', str(address)))
        self.players[pl_id].time = 0
        self.players[pl_id].spawn(100, 300)
        self.players_pack[pl_id] = proto.Player()
        self.players_pack[pl_id].id = pl_id
        self.player_to_pack(pl_id)
        self.timers[pl_id] = 0
        #send info do newly connected player
        own = proto.Player()
        own.type = proto.mapupdate
        own.id = pl_id
        self.transport.write(own.SerializeToString(), address)
        #send other players to player
        self.players_pack[pl_id].type = proto.newplayer
        for idx, p in self.players.iteritems():
            if idx != pl_id:
                print 'why even'
                other = self.players_pack[idx]
                other.type = proto.newplayer
                self.transport.write(other.SerializeToString(),
                                     self.players[pl_id].address)
                other.type = proto.update
                self.transport.write(self.players_pack[pl_id].SerializeToString(), p.address)
        self.players_pack[pl_id].type = proto.update
