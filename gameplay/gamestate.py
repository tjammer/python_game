from network_utils import protocol_pb2 as proto


class GamestateManager(object):
    """docstring for GamestateManager"""
    def __init__(self, allgenfunc, ackman, players):
        super(GamestateManager, self).__init__()
        #function which return generator of all players and specs
        self.all = allgenfunc
        self.ackman = ackman
        self.ingame = players
        #self.gameType = Duel()

    def update(self, dt):
        for player in self.ingame.itervalues():
            if player.state.isDead:
                player.state.isDead -= dt
                if player.state.isDead <= 0.0 or (player.state.isDead < 4
                                                  and player.input.att):
                    self.spawn(player)

    def damage_player(self, player, proj):
        #armor absorbs 2/3 of dmg
        hpdmg = proj.dmg / 3
        armordmg = hpdmg * 2 + proj.dmg % 3
        player.state.armor -= armordmg
        if player.state.armor < 0:
            player.state.hp += player.state.armor
            player.state.armor = 0
        player.state.hp -= hpdmg
        if player.state.hp <= 0:
            self.kill(player, proj)

    def kill(self, player, proj):
        if not player.state.isDead:
            player.die()
            msg = proto.Message()
            msg.type = proto.stateUpdate
            plr = proto.Player()
            plr.id = player.id
            msg.player.CopyFrom(plr)
            projectile = proto.Projectile()
            projectile.type = proj.type
            projectile.playerId = proj.id
            msg.projectile.CopyFrom(projectile)
            msg.gameState = proto.isDead
            for player_ in self.all():
                self.ackman.send_rel(msg, player_.address)

    def join(self, data):
        id = data.player.id
        if len(self.ingame) < 2 and id not in self.ingame:
            msg = proto.Message()
            msg.type = proto.stateUpdate
            plr = proto.Player()
            plr.id = id
            msg.player.CopyFrom(plr)
            msg.gameState = proto.wantsJoin
            for player in self.all():
                self.ackman.send_rel(msg, player.address)
            return True
        return False

    def spec(self, data):
        id = data.player.id
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = id
        msg.player.CopyFrom(plr)
        msg.gameState = proto.goesSpec
        for player in self.all():
            self.ackman.send_rel(msg, player.address)

    def spawn(self, player):
        player.spawn(100, 200)
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = player.id
        plr.posx = player.state.pos.x
        plr.posy = player.state.pos.y
        msg.player.CopyFrom(plr)
        msg.gameState = proto.spawns
        for player_ in self.all():
            self.ackman.send_rel(msg, player_.address)
