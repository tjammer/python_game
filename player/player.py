from movement import Movement
from graphics.primitives import Rect
from network_utils import protocol_pb2 as proto
from collision.vector import magnitude


class player(object):
    """docstring for player"""
    def __init__(self):
        super(player, self).__init__()
        self.pos = [50, 50]
        self.Move = Movement(*self.pos)
        self.vel = []
     # spawning player at 0,0, width 32 = 1280 / 40. and height 72 = 720/10.
        self.Rect = Rect(0, 0, 32, 72, (0, .8, 1.))

        self.listeners = {}

    def update(self, dt):
        self.vel, self.pos = self.Move.update(dt, self.pos)
        self.Rect.update(*self.pos)
        self.send_messsage('changed_pos', [self.pos[0], self.vel[0]])
        self.send_messsage('input', (self.Move.input, dt, self.pos, self.vel))

    def update_local(self, dt):
        self.Rect.update(*self.pos)
        self.send_messsage('changed_pos', [self.pos[0], self.vel[0]])
        self.send_messsage('input', (self.Move.input, dt, self.pos, self.vel))

    def client_update(self, data):
        easing = .8
        snapping_distance = 20

        diff = [data.posx - self.pos[0], data.posy - self.pos[1]]
        len_diff = magnitude(*diff)

        if len_diff > snapping_distance:
            self.pos = [data.posx, data.posy]
        elif len_diff > .1:
            self.pos[0] += diff[0] * easing
            self.pos[1] += diff[1] * easing
        self.vel = [data.velx, data.vely]

    def draw(self):
        self.Rect.draw()

    def resolve_collision(self, ovrlap, axis, angle):
        self.pos[0] = self.Rect.x1 - ovrlap * axis[0]
        self.pos[1] = self.Rect.y1 - ovrlap * axis[1]
        self.vel[0] *= axis[1] > 0
        self.vel[1] *= axis[0] > 0
        self.Rect.update(*self.pos)
        self.Move.resolve_coll(self.pos, self.vel)
        if axis[1] > 0 and ovrlap < 0:
            self.Move.conds['on_ground'] = True
            self.Move.angle = angle

    def spawn(self, x, y):
        self.pos = [x, y]
        self.vel = [0, 0]

    def register(self, listener, events):
        self.listeners[listener] = events

    def send_messsage(self, event, msg):
        for listener, events in self.listeners.items():
            if event in events:
                try:
                    listener(event, msg)
                except (Exception, ):
                    self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]
