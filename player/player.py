from movement import Movement
from graphics.primitives import Rect
from collision.vector import magnitude
from network_utils import protocol_pb2 as proto
from state import vec2, state
from menu.menu_events import Events


class player(Events):
    """docstring for player"""
    def __init__(self):
        super(player, self).__init__()
        self.state = state(vec2(50, 50), vec2(0, 0), 100)
        self.Move = Movement(*self.state.pos)
     # spawning player at 0,0, width 32 = 1280 / 40. and height 72 = 720/10.
        self.Rect = Rect(0, 0, 32, 72, (0, .8, 1.))
        #input will be assigned by windowmanager class
        self.input = proto.input()

        self.listeners = {}

    def update(self, dt, state=False, input=False):
        if not state:
            state = self.state
        if not input:
            input = self.input
        self.state.vel, self.state.pos = self.Move.update(dt,
                                                          state.pos, state.vel,
                                                          input)
        self.Rect.update(*self.state.pos)

    def update_state(self):
        self.state.pos = self.pos
        self.state.vel = self.vel

    def client_update(self, data):
        easing = .8
        snapping_distance = 20

        diff = [data.posx - self.state.pos[0], data.posy - self.state.pos[1]]
        len_diff = magnitude(*diff)

        if len_diff > snapping_distance:
            self.state.pos = [data.posx, data.posy]
        elif len_diff > .1:
            self.state.pos[0] += diff[0] * easing
            self.state.pos[1] += diff[1] * easing
        self.state.vel = [data.velx, data.vely]

    def draw(self):
        self.Rect.draw()

    def resolve_collision(self, ovrlap, axis, angle):
        self.state.pos[0] = self.Rect.x1 - ovrlap * axis[0]
        self.state.pos[1] = self.Rect.y1 - ovrlap * axis[1]
        self.state.vel[0] *= axis[1] > 0
        self.state.vel[1] *= axis[0] > 0
        self.Rect.update(*self.state.pos)
        self.Move.resolve_coll(self.state.pos, self.state.vel)
        if axis[1] > 0 and ovrlap < 0:
            self.Move.conds['on_ground'] = True
            self.Move.angle = angle

    def spawn(self, x, y):
        self.state.pos = vec2(x, y)
        self.state.vel = vec2(0, 0)
