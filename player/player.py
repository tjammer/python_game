from movement import Move
from graphics.primitives import Rect


class player(object):
    """docstring for player"""
    def __init__(self):
        super(player, self).__init__()
        self.Move = Move()
        self.pos = []
        self.vel = []
     # spawning player at 0,0, width 32 = 1280 / 40. and height 72 = 720/10.
        self.Rect = Rect(0, 0, 32, 72, (0, .8, 1.))

        self.listeners = {}

    def update(self, dt):
        self.vel, self.pos = self.Move.update(dt)
        self.Rect.update(*self.pos)
        self.send_messsage('changed_pos', [self.pos[0], self.Move.vel[0]])

    def draw(self):
        self.Rect.draw()

    def register(self, listener, events):
        self.listeners[listener] = events

    def send_messsage(self, event, msg):
        for listener, events in self.listeners.items():
            if event in events:
                listener(event, msg)