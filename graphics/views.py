from player.cvec2 import cvec2 as vec2
from model import Model
from os import path
from gameplay.weapons import weaponcolors

weaponcolors = {int(key[1:]) + 1: [c / 255. for c in color] + [1.]
                for key, color in weaponcolors.iteritems()}


class DrawablePlayer(object):
    """docstring for DrawablePlayer"""
    def __init__(self, player, batch, fac):
        super(DrawablePlayer, self).__init__()
        self.state = player.state
        # self.rect = player.rect.copy()
        # self.batch = batch
        self.model = Model(path.join('graphics', 'metatest.dae'), fac.x)
        self.model.change_color([c / 255. for c in player.rect.color] + [1.])
        self.weapon = None
        # self.scale(fac)

    def scale(self, fac):
        self.rect.pos *= fac
        self.rect.width *= fac.x
        self.rect.height *= fac.y
        self.rect.add(self.batch)

    def update(self, state, fac):
        pos = vec2(*state.pos) * fac
        # self.rect.update(*pos)
        self.state = state
        self.state.mpos = state.mpos - state.pos - vec2(16, 54)
        self.state.pos = pos

    def animate(self, dt):
        self.model.update(dt, self.state)

    def update_weapon(self, weapon):
        if weapon != self.weapon:
            self.model.update_weapon(weaponcolors[weapon])
            self.weapon = weapon

    def attack(self):
        self.model.start_attack()

    def draw(self, mvp):
        self.model.draw(mvp)

    def remove(self):
        # self.rect.remove()
        self.model.remove()
