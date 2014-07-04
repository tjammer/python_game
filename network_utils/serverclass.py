from twisted.internet.protocol import DatagramProtocol
import protocol_pb2 as proto
from maps.map import Map
from player.player import Player
from datetime import datetime
from gameplay.weapons import ProjectileManager


class GameServer(DatagramProtocol):
    """docstring for GameServer"""
    def __init__(self):
        # super(GameServer, self).__init__()
        self.players = {}
        self.players_pack = {}
        self.projectiles = ProjectileManager()
        self.map = Map('testmap', server=True)
        self.mxdt = .03

    def datagramReceived(self, datagram, address):
        data = proto.input()
        data.ParseFromString(datagram)
        if data.type == proto.newplayer:
            pl_id = self.get_id()
            self.init_player(data, address, pl_id)
        elif data.type == proto.update and data.id == self.find_id(address):
            self.players[data.id].timer = 0
            self.get_input(data)
            dt = data.time - self.players[data.id].time
            if dt > 0:
                dt = (dt / 10000.)
                dt = dt if dt < self.mxdt else self.mxdt
                # update movement
                self.players[data.id].update(dt)
                self.collide(data.id)
                self.players[data.id].time = data.time
                self.player_to_pack(data.id)
        elif (data.type == proto.disconnect and
              data.id == self.find_id(address)):
            print ' '.join((str(datetime.now()),
                           self.players[data.id].name, 'disconnected'))
            self.disc_player(data.id)

    def update(self, dt):
        keys = []
        for key, player in self.players.iteritems():
            player.timer += dt
            if player.timer > 10:
                keys.append(key)
        for key in keys:
            print ' '.join((str(datetime.now()),
                           self.players[key].name, 'timed out'))
            self.disc_player(key)
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
        self.players[data.id].input = data

    def collide(self, idx):
        for keys in self.players:
            if keys != idx:
                coll = self.players[idx].rect.collides(self.players[keys].rect)
                if coll:
                    ovr, axis = coll
                    self.players[idx].resolve_collision(ovr, axis, 0)
        #collide with players first to not get collided into wall
        for rect in self.map.quad_tree.retrieve([], self.players[idx].rect):
            coll = self.players[idx].rect.collides(rect)
            if coll:
                ovr, axis = coll
                self.players[idx].resolve_collision(ovr, axis, rect.angle)

    def collide_proj(self):
        pass

    def init_player(self, data, address, pl_id):
        #check if name already exists
        name = data.name
        i = 1
        while name in [p.name for p in self.players.itervalues()]:
            name = data.name + '_' + str(i)
            i += 1
        self.players[pl_id] = Player(server=True)
        self.players[pl_id].address = address
        self.players[pl_id].name = name
        print ' '.join((str(datetime.now()),
                        self.players[pl_id].name,
                        'joined the server', str(address)))
        self.players[pl_id].time = 0
        self.players[pl_id].spawn(100, 300)
        self.players_pack[pl_id] = proto.Player()
        self.players_pack[pl_id].id = pl_id
        self.player_to_pack(pl_id)
        self.players[pl_id].timer = 0
        #send info do newly connected player
        own = proto.Player()
        own.type = proto.mapupdate
        own.id = pl_id
        self.transport.write(own.SerializeToString(), address)
        #send other players to player
        self.players_pack[pl_id].type = proto.newplayer
        for idx, p in self.players.iteritems():
            if idx != pl_id:
                other = self.players_pack[idx]
                other.type = proto.newplayer
                self.transport.write(other.SerializeToString(),
                                     self.players[pl_id].address)
                other.type = proto.update
                self.transport.write(self.players_pack[pl_id].SerializeToString(), p.address)
        self.players_pack[pl_id].type = proto.update

    def disc_player(self, id):
        del self.players[id], self.players_pack[id]
        disc = proto.Player()
        disc.type = proto.disconnect
        disc.id = id
        for idx, p in self.players.iteritems():
            self.transport.write(disc.SerializeToString(), p.address)
