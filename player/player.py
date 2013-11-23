from movement import Move
from graphics.primitives import Rect


class player(object):
    """docstring for player"""
    def __init__(self):
        super(player, self).__init__()
        self.Move = Move()
        self.pos = []
        self.vel = []
        self.Rect = Rect(0, 0, 32, 72, (0, .8, 1.))

    def update(self, dt):
        self.vel, self.pos = self.Move.update(dt)
        self.Rect.update(*self.pos)

    def draw(self):
        self.Rect.draw()
