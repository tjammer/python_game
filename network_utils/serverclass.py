from twisted.internet.protocol import DatagramProtocol
import protocol_pb2 as proto
from maps.map import Map
from player.player import Player
from datetime import datetime
from gameplay.weapons import ProjectileManager
from gameplay.gamestate import GamestateManager
from itertools import chain
from reliable import AckManager


class GameServer(DatagramProtocol):
    """docstring for GameServer"""
    def __init__(self):
        # super(GameServer, self).__init__()
        self.players = {}
        self.players_pack = {}
        self.specs = {}
        self.map = Map('phrantic', server=True)
        self.ackman = AckManager()
        self.gamestate = GamestateManager(self.allgen, self.ackman,
                                          self.players, self.map.spawns,
                                          self.map.items, self.spec_player)
        self.projectiles = ProjectileManager(self.players, self.map,
                                             self.gamestate.damage_player,
                                             self.allgen)
        self.mxdt = .03

    def datagramReceived(self, datagram, address):
        data = proto.Message()
        data.ParseFromString(datagram)
        if data.type == proto.newPlayer:
            self.ackman.respond(data, address)
            if self.not_online(address):
                pl_id = self.get_id()
                self.init_player(data, address, pl_id)
        elif data.type == proto.playerUpdate and self.isplayer(data, address):
            self.players[data.input.id].timer = 0
            #self.get_input(data.input)
            self.players[data.input.id].input = data.input
            dt = data.input.time - self.players[data.input.id].time
            if dt > 0:
                dt = (dt / 1000000.)
                dt = dt if dt < self.mxdt else self.mxdt
                # update movement
                self.players[data.input.id].update(dt,
                                                   self.rectgen(data.input.id))
                self.players[data.input.id].time = data.input.time
                self.player_to_pack(data.input.id)
        elif data.type == proto.disconnect and self.isonline(data, address):
            self.ackman.respond(data, address)
            self.disc_player(data.input.id)
        elif data.type == proto.ackResponse and self.isonline(data, address):
            self.ackman.receive_ack(data)
        elif data.type == proto.stateUpdate and self.isonline(data, address):
            self.ackman.respond(data, address)
            if data.gameState == proto.wantsJoin:
                if self.gamestate.join(data):
                    self.join_player(data.player.id)
            elif data.gameState == proto.goesSpec:
                self.gamestate.spec(data)
                #self.spec_player(data.player.id)
            elif data.gameState == proto.isReady:
                self.gamestate.ready_up(data)
        elif data.type == proto.chat:
            self.ackman.respond(data, address)
            self.gamestate.rec_chat(data, address)

    def update(self, dt):
        keys = []
        for key, player in self.players.iteritems():
            player.timer += dt
            if player.timer > 10:
                keys.append(key)

        for key, player in self.specs.iteritems():
            player.timer += dt
            if player.timer > 10:
                keys.append(key)
        for key in keys:
            self.disc_player(key)
        self.projectiles.update(dt)
        self.gamestate.update(dt)
        self.send_all()
        self.ackman.update(dt)

    def send_all(self):
        for player_ in self.allgen():
            for idx_, pack in self.players_pack.iteritems():
                msg = proto.Message()
                msg.type = proto.playerUpdate
                msg.player.CopyFrom(pack)
                msg.input.CopyFrom(self.players[idx_].input)
                self.transport.write(msg.SerializeToString(), player_.address)

    #find next available id
    def get_id(self):
        idx = 1
        while idx in self.players or idx in self.specs:
            idx += 1
        return idx

    def isplayer(self, data, address):
        id = data.input.id
        for id in self.players:
            if address == self.players[id].address:
                return id
        for id in self.specs:
            if address == self.specs[id].address:
                self.specs[id].timer = 0
        return False

    def isonline(self, data, address):
        id = data.input.id
        if id in self.players:
            if self.players[id].address == address:
                return True
        elif id in self.specs:
            if self.specs[id].address == address:
                return True
        return False

    def player_to_pack(self, idx):
        pp = self.players_pack[idx]
        pp.posx = self.players[idx].state.pos.x
        pp.posy = self.players[idx].state.pos.y
        pp.velx = self.players[idx].state.vel.x
        pp.vely = self.players[idx].state.vel.y
        pp.hp = self.players[idx].state.hp
        pp.armor = self.players[idx].state.armor
        pp.time = self.players[idx].time
        pp.mState.CopyFrom(self.players[idx].state.conds)
        pp.ammo, pp.weapon = self.players[idx].weapons.pack_ammo_weapon()

    def get_input(self, data):
        self.players[data.id].input = data

    def collide(self, idx):
        colled = False

        for rect in self.rectgen(idx):
            coll = self.players[idx].rect.collides(rect)
            if coll:
                colled = True
                ovr, axis = coll
                self.players[idx].resolve_collision(ovr, axis, 0)
        if not colled:
            self.players[idx].determine_state()

    def init_player(self, data, address, pl_id):
        #check if name already exists
        name = data.player.chat
        i = 1
        namegen = chain(self.players.itervalues(), self.specs.itervalues())
        while name in [p.name for p in namegen]:
            name = data.player.chat + '_' + str(i)
            i += 1
        player = Player(True, self.projectiles.add_projectile, pl_id)
        player.timer = 0
        player.address = address
        player.name = name
        player.colstring = data.input.name
        print ' '.join((str(datetime.now()),
                        player.name, str(pl_id),
                        'joined the server', str(address)))
        player.time = 0
        self.specs[pl_id] = player
        tosendplayer = proto.Player()
        tosendplayer.id = pl_id
        tosendplayer.chat = player.name
        #send info do newly connected player
        own = proto.Message()
        player = proto.Player()
        own.type = proto.connectResponse
        player.id = pl_id
        player.chat = self.specs[pl_id].name
        inpt = proto.Input()
        inpt.time = 0
        inpt.name = self.map.name
        own.input.CopyFrom(inpt)
        own.player.CopyFrom(player)
        self.ackman.send_rel(own, address)
        #send other players to player
        for idx, p in self.players.iteritems():
            if idx != pl_id:
                #other players
                other = proto.Message()
                player = self.players_pack[idx]
                player.chat = p.name
                other.type = proto.newPlayer
                other.player.CopyFrom(player)
                other.gameState = proto.wantsJoin
                inpt = proto.Input()
                inpt.name = p.colstring
                other.input.CopyFrom(inpt)
                self.ackman.send_rel(other, address)
                #other.type = proto.playerUpdate
                new = proto.Message()
                new.type = proto.newPlayer
                #player = self.players_pack[pl_id]
                new.gameState = proto.goesSpec
                new.player.CopyFrom(tosendplayer)
                inpt = proto.Input()
                inpt.name = self.specs[pl_id].colstring
                new.input.CopyFrom(inpt)
                self.ackman.send_rel(new, p.address)
        for idx, p in self.specs.iteritems():
            if idx != pl_id:
                other = proto.Message()
                player = proto.Player()
                player.id = idx
                player.chat = p.name
                other.type = proto.newPlayer
                other.player.CopyFrom(player)
                other.gameState = proto.goesSpec
                inpt = proto.Input()
                inpt.name = p.colstring
                other.input.CopyFrom(inpt)
                self.ackman.send_rel(other, address)

                new = proto.Message()
                new.type = proto.newPlayer
                #player = self.players_pack[pl_id]
                new.gameState = proto.goesSpec
                new.player.CopyFrom(tosendplayer)
                inpt = proto.Input()
                inpt.name = self.specs[pl_id].colstring
                new.input.CopyFrom(inpt)
                self.ackman.send_rel(new, p.address)
        #TODO: send map status
        self.map.items.send_mapstate(self.gamestate.send_mapupdate, address)

    def disc_player(self, id):
        if id in self.players:
            print ' '.join((str(datetime.now()), self.players[id].name,
                            'disconnected'))
            self.gamestate.leave(id)
            del self.players[id], self.players_pack[id]
        elif id in self.specs:
            print ' '.join((str(datetime.now()), self.specs[id].name,
                            'disconnected'))
            del self.specs[id]
        disc = proto.Message()
        disc.type = proto.disconnect
        player = proto.Player()
        player.id = id
        disc.player.CopyFrom(player)
        for idx, p in chain(self.players.iteritems(), self.specs.iteritems()):
            #self.transport.write(disc.SerializeToString(), p.address)
            self.ackman.send_rel(disc, p.address)

    def join_player(self, id):
        self.players[id] = self.specs[id]
        del self.specs[id]
        self.gamestate.spawn(self.players[id])
        #self.players[id].spawn(100, 300)
        self.players_pack[id] = proto.Player()
        self.players_pack[id].id = id
        self.player_to_pack(id)
        self.gamestate.to_team(id)

    def spec_player(self, id):
        self.specs[id] = self.players[id]
        self.specs[id].ready = False
        self.gamestate.leave(id)
        del self.players[id], self.players_pack[id]

    def rectgen(self, idx=-1):
        playergen = (player.rect for key, player in self.players.iteritems()
                     if key != idx)
        mapgen = (rect for rect in self.map.quad_tree.retrieve([],
                  self.players[idx].rect))
        return chain(playergen, mapgen)

    def allgen(self):
        playergen = (player for player in self.players.itervalues())
        specgen = (spec for spec in self.specs.itervalues())
        return chain(playergen, specgen)

    def not_online(self, address):
        for p in self.allgen():
            if address == p.address:
                return False
        return True
