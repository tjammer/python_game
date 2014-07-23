from network_utils import protocol_pb2 as proto

class GamestateManager(object):
    """docstring for GamestateManager"""
    def __init__(self, allgenfunc, ackman):
        super(GamestateManager, self).__init__()
        #function which return generator of all players and specs
        self.all = allgenfunc
        self.ackman = ackman
        self.ingame = []
        #self.gameType = Duel()

    def damage_player(self, player, dmg):
        #armor absorbs 2/3 of dmg
        hpdmg = dmg / 3
        armordmg = hpdmg * 2 + dmg % 3
        player.state.armor -= armordmg
        if player.state.armor < 0:
            player.state.hp += player.state.armor
            player.state.armor = 0
        player.state.hp -= hpdmg
        if player.state.hp <= 0:
            self.kill(player)

    def kill(self, player):
        player.die()

    def join(self, data):
        id = data.player.id
        if len(self.ingame) < 2 and id not in self.ingame:
            self.ingame.append(id)
            for player in self.all():
                msg = proto.Message()
                msg.type = proto.stateUpdate
                plr = proto.Player()
                plr.id = id
                msg.player.CopyFrom(plr)
                msg.gameState = proto.wantsJoin
                self.ackman.send_rel(msg, player.address)
            return True
        return False

    def disconnect_player(self, id):
        self.ingame.remove(id)
