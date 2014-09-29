from network_utils import protocol_pb2 as proto
from random import choice


def duel_calc_score(killed, killer):
    if killed != killer:
        killer.score += 1
    else:
        killer.score -= 1


class GamestateManager(object):
    """docstring for GamestateManager"""
    def __init__(self, allgenfunc, ackman, players, spawns, items, send_spec):
        super(GamestateManager, self).__init__()
        #function which return generator of all players and specs
        self.all = allgenfunc
        self.ackman = ackman
        self.ingame = players
        #self.gameType = Duel()
        self.a = Team()
        self.b = Team()
        self.gamestate = proto.warmUp
        self.gametime = 0
        self.spawns = spawns
        for spawn in spawns:
            spawn.active = False
        self.items = items
        self.ticks = 0
        self.send_spec = send_spec
        self.dueltime = 300

    def update(self, dt):
        self.ticks += dt
        for player in self.ingame.itervalues():
            if player.state.isDead:
                player.state.isDead -= dt
                if player.state.isDead <= 0.0 or (player.state.isDead < 4
                                                  and player.input.att):
                    self.spawn(player)
            else:
                if not self.gamestate == proto.countDown:
                    for item in self.items:
                        if player.rect.overlaps(item):
                            if self.items.apply(player, item):
                                self.send_mapupdate(item, player)
            if self.ticks >= 1:
                self.tick(player)
        for spawn in self.spawns:
            if spawn.active:
                spawn.active -= dt
                if spawn.active <= 0:
                    spawn.active = False
        if self.gametime > 0:
            self.gametime -= dt
            if self.gametime < 0:
                self.gametime = 0
        if self.gamestate == proto.countDown and self.gametime == 0:
            self.start_game()
        if self.gamestate == proto.inProgress and self.gametime == 0:
            if not self.a.score == self.b.score:
                self.stop_game()
            else:
                self.gametime = 60
                self.send_overtime()
        elif self.gamestate == proto.warmUp and not self.gametime:
            if len(self.ingame) == 2:
                self.countdown()
        elif self.gamestate == proto.gameOver and self.gametime == 0:
            self.to_warmup()
        self.items.update(dt, self.send_mapupdate)
        if self.ticks >= 1:
            self.ticks = 0

    def update_player(self, dt, id, rectgen):
        if not self.gamestate == proto.gameOver:
            self.ingame[id].update(dt, rectgen)

    def damage_player(self, player, proj):
        if not player.state.isDead:
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
            msg.gameTime = self.gametime
            self.score(player.id, proj.id)
            for player_ in self.all():
                self.ackman.send_rel(msg, player_.address)

    def join(self, data):
        id = data.player.id
        if self.gamestate == proto.gameOver:
            return False
        if len(self.ingame) < 2 and id not in self.ingame:
            msg = proto.Message()
            msg.type = proto.stateUpdate
            plr = proto.Player()
            plr.id = id
            msg.player.CopyFrom(plr)
            msg.gameState = proto.wantsJoin
            msg.gameTime = self.gametime
            for player in self.all():
                self.ackman.send_rel(msg, player.address)
            if len(self.ingame) < 2:
                self.gametime = 60
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
        #if self.gamestate == proto.countDown or
        #self.gamestate == proto.inProgress:
        if self.gamestate in [proto.countDown, proto.inProgress]:
            self.to_warmup()

    def spec(self, id):
        if self.gamestate == proto.gameOver:
            return
        if id in self.ingame:
            msg = proto.Message()
            msg.type = proto.stateUpdate
            plr = proto.Player()
            plr.id = id
            msg.player.CopyFrom(plr)
            msg.gameState = proto.goesSpec
            msg.gameTime = self.gametime
            for player in self.all():
                self.ackman.send_rel(msg, player.address)
            self.send_spec(id)

    def spawn(self, player):
        try:
            spawnp = choice([spawn for spawn in self.spawns
                            if not spawn.active])
        except IndexError:
            spawnp = choice(self.spawns)
        self.spawns[self.spawns.index(spawnp)].active = 2
        player.spawn(*spawnp)
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = player.id
        plr.posx = player.state.pos.x
        plr.posy = player.state.pos.y
        msg.player.CopyFrom(plr)
        msg.gameState = proto.spawns
        msg.gameTime = self.gametime
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

    def ready_up(self, data):
        if self.gamestate == proto.warmUp:
            id = data.player.id
            self.ingame[id].ready = True
            if len([plr for plr in self.ingame.itervalues()
                   if plr.ready]) == 2:
                self.countdown()
            else:
                msg = proto.Message()
                msg.type = proto.stateUpdate
                plr = proto.Player()
                plr.id = id
                plr.chat = self.ingame[id].name
                msg.player.CopyFrom(plr)
                msg.gameState = proto.isReady
                msg.gameTime = self.gametime
                for player in self.all():
                    self.ackman.send_rel(msg, player.address)

    def countdown(self):
        self.gametime = 10
        self.gamestate = proto.countDown
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = 0
        msg.player.CopyFrom(plr)
        msg.gameState = proto.countDown
        msg.gameTime = self.gametime
        for player in self.all():
            self.ackman.send_rel(msg, player.address)
        for player in self.ingame.itervalues():
            player.freeze()

    def send_overtime(self):
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = 0
        msg.player.CopyFrom(plr)
        msg.gameState = proto.overTime
        msg.gameTime = self.gametime
        for player in self.all():
            self.ackman.send_rel(msg, player.address)

    def start_game(self):
        self.gametime = self.dueltime
        self.gamestate = proto.inProgress
        for item in self.items.get_inactive():
            item.inactive = False
            self.send_mapupdate(item)
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = 0
        msg.player.CopyFrom(plr)
        msg.gameState = proto.inProgress
        msg.gameTime = self.gametime
        for player in self.all():
            self.ackman.send_rel(msg, player.address)
        for player in self.ingame.itervalues():
            self.spawn(player)

    def to_warmup(self):
        for player in self.ingame.itervalues():
            player.ready = False
            self.spawn(player)
        for team in (self.a, self.b):
            team.score = 0
        self.gametime = 180
        self.gamestate = proto.warmUp
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = 0
        msg.player.CopyFrom(plr)
        msg.gameState = proto.warmUp
        msg.gameTime = self.gametime
        for player in self.all():
            self.ackman.send_rel(msg, player.address)

    def stop_game(self):
        self.gamestate = proto.gameOver
        self.gametime = 10
        msg = proto.Message()
        msg.type = proto.stateUpdate
        msg.gameState = proto.gameOver
        msg.gameTime = self.gametime
        for player in self.all():
            self.ackman.send_rel(msg, player.address)

    def send_mapupdate(self, item, player_=False, address=None):
        msg = proto.Message()
        msg.type = proto.mapUpdate
        plr = proto.Player()
        if player_:
            plr.id = player_.id
        else:
            plr.id = -1
        msg.player.CopyFrom(plr)
        msg.gameState = proto.mapUpdate
        msg.gameTime = self.gametime
        input = proto.Input()
        input.time = 0
        input.id = item.ind
        #spawn
        if player_:
            input.right = False
        else:
            input.right = True
        msg.input.CopyFrom(input)
        if not address:
            for player in self.all():
                self.ackman.send_rel(msg, player.address)
        else:
            self.ackman.send_rel(msg, address)

    def tick(self, player):
        if player.state.hp > 100:
            player.state.hp -= 1

    def rec_chat(self, data, address):
        for player in self.all():
            self.ackman.send_rel(data, player.address)

    def send_current_gs(self, address):
        msg = proto.Message()
        msg.type = proto.stateUpdate
        msg.gameState = self.gamestate
        msg.gameTime = self.gametime
        self.ackman.send_rel(msg, address)


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
        self.name = player.name

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
        self.gametime = 10

    def update(self, dt):
        if self.gametime > 0:
            self.gametime -= dt
            if self.gametime < 0:
                self.gametime = False
        self.hudhook(time=self.gametime)

    def leave(self, id):
        if id in self.a:
            self.a.leave(id)
            self.a.name = '_'
            self.hudhook(name=(True, '_'))
        else:
            self.b.leave(id)
            self.b.name = '_'
            self.hudhook(name=(False, '_'))
        self.scorehook(0, 0)

    def score(self, killed, killer, weapon=False):
        for team in (self.a, self.b):
            if killed in team and killer in team:
                if self.gamestate == proto.inProgress:
                    team.score -= 1
                krn = team.name
                kdn = team.name
                break
            elif killer in team:
                if self.gamestate == proto.inProgress:
                    team.score += 1
                krn = team.name
            else:
                kdn = team.name
        self.scorehook(self.a.score, self.b.score, msg=(weapon, krn, kdn))

    def init_self(self, id, gs):
        self.ownid = id
        self.gamestate = gs

    def add_self(self, ownplayer):
        if len(self.b) == 0:
            self.b = self.a
            self.hudhook(name=(False, self.b.name))
        self.a = Team()
        self.a.join(ownplayer)
        self.hudhook(name=(True, ownplayer.name))
        self.scorehook(self.a.score, self.b.score)

    def to_team(self, id):
        if len(self.a) == 0:
            self.a.join(self.players[id])
            self.hudhook(name=(True, self.players[id].name))
        else:
            self.b.join(self.players[id])
            self.hudhook(name=(False, self.players[id].name))
        self.reset_score()
        self.scorehook(self.a.score, self.b.score)

    def reset_score(self):
        self.a.score = 0
        self.b.score = 0

    def set_time(self, time):
        self.gametime = time

    def is_ready(self, id, name):
        text = ' '.join((name, 'is ready!'))
        self.hudhook(text=text)

    def show_score(self):
        self.scorehook(self.a.score, self.b.score, scoreboard=True)

    def start_game(self):
        self.gamestate = proto.inProgress

    def to_warmup(self):
        self.gamestate = proto.warmUp
        self.reset_score()
        self.scorehook(self.a.score, self.b.score)

    def count_down(self):
        text = 'all players are ready! prepare to fight!'
        self.hudhook(text=text)
