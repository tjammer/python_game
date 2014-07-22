class GamestateManager(object):
    """docstring for GamestateManager"""
    def __init__(self, allgenfunc, ackman):
        super(GamestateManager, self).__init__()
        #function which return generator of all players and specs
        self.all = allgenfunc
        self.ackman = ackman

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
