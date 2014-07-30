from network_utils import protocol_pb2 as proto


def duel_calc_score(killed, killer):
    if killed != killer:
        killer.score += 1
    else:
        killer.score -= 1


class GamestateManager(object):
    """docstring for GamestateManager"""
    def __init__(self, allgenfunc, ackman, players):
        super(GamestateManager, self).__init__()
        #function which return generator of all players and specs
        self.all = allgenfunc
        self.ackman = ackman
        self.ingame = players
        #self.gameType = Duel()
        self.a = Team()
        self.b = Team()
        self.gamestate = proto.warmUp

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

    def to_team(self, id):
        if len(self.a) == 0:
            self.a.join(self.ingame[id])
        else:
            self.b.join(self.ingame[id])

    def leave(self, id):
        if id in self.a:
            self.a.leave(id)
        else:
            self.b.leave(id)

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

    def score(self, killed, killer):
        if self.gamestate == proto.inProgress:
            for team in (self.a, self.b):
                if killed in team and killer in team:
                    team.score -= 1
                    return 0
                elif killer in team:
                    team.score += 1


class Team(object):
    """docstring for Team"""
    def __init__(self):
        super(Team, self).__init__()
        self.players = {}
        self.score = 0
        self.name = '_'

    def __iter__(self):
        return self.players.iterkeys()

    def __len__(self):
        return len(self.players)

    def __repr__(self):
        return str([pl.id for pl in self.players.itervalues()])

    def join(self, player):
        self.players[player.id] = player

    def leave(self, id):
        del self.players[id]


class GameStateViewer(object):
    """docstring for GameStateViewer"""
    def __init__(self, players, hudhook, scorehook):
        super(GameStateViewer, self).__init__()
        self.players = players
        self.a = Team()
        self.b = Team()
        self.ownid = -1
        self.gamestate = proto.warmUp
        self.hudhook = hudhook
        self.scorehook = scorehook

    def leave(self, id):
        if id in self.a:
            self.a.leave(id)
        else:
            self.b.leave(id)
            self.hudhook(score='-')

    def score(self, killed, killer, weapon=False):
        if self.gamestate == proto.warmUp:
            for team in (self.a, self.b):
                if killed in team and killer in team:
                    team.score -= 1
                    break
                elif killer in team:
                    team.score += 1
        self.scorehook(self.a.score, self.b.score, msg=weapon)

    def init_self(self, id):
        self.ownid = id

    def add_self(self, ownplayer):
        if len(self.b) == 0:
            self.b = self.a
        self.a = Team()
        self.a.join(ownplayer)
        self.scorehook(self.a.score, self.b.score)

    def to_team(self, id):
        if len(self.a) == 0:
            self.a.join(self.players[id])
        else:
            self.b.join(self.players[id])
            self.hudhook(score=self.players[id].name)
        self.reset_score()

    def reset_score(self):
        self.a.score = 0
        self.b.score = 0
