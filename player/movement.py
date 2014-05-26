import math
from network_utils import protocol_pb2 as proto


class Movement(object):
    """docstring for Movement"""
    def __init__(self, x, y):
        super(Movement, self).__init__()
        self.pos = [x, y]
        self.vel = [0, 0]
        self.gravity = 4000.
        self.normal_accel = 500.
        self.boost_accel = 20.
        self.turn_multplier = 4.
        self.jump_vel = 1500.
        self.max_vel = 500
        self.angle = 0
        self.conds = {'can_jump': False, 'on_ground': False}

        self.input = proto.input()

    def update(self, dt, pos):
        self.calc_vel(dt)
        self.step(dt, pos)
        self.set_conds()
        return self.vel, self.pos

    def step(self, dt, pos):
        if not self.conds['on_ground']:
            self.vel[1] -= self.gravity * dt
        for i, j in enumerate(self.pos):
            self.pos[i] = pos[i] + self.vel[i] * dt

    def calc_vel(self, dt):
        #check left right
        if self.input.right and not self.input.left:
            sign = 1
        elif self.input.left and not self.input.right:
            sign = -1
        else:
            self.vel[0] = 0
            sign = 0
        self.curr_sign = self.sign_of(self.vel[0])
        v = self.normal_accel
        if self.curr_sign != 0 and self.curr_sign != sign:
            v *= self.turn_multplier
        self.vel[0] += v * sign * dt
        self.vel[1] += v * math.tan(self.angle) * sign * dt
        if abs(self.vel[0]) > self.max_vel:
            self.vel[0] = self.max_vel * self.curr_sign
        #check jump
        if self.conds['can_jump'] and self.input.up:
            self.vel[1] = self.jump_vel
            self.conds['can_jump'] = False
        #in air
        if not self.input.up and self.vel[1] > 0:
            self.vel[1] = 0

    def set_conds(self):
        if self.conds['on_ground']:
            self.conds['can_jump'] = True
        self.conds['on_ground'] = False

    def sign_of(self, num):
        if num > 0:
            return 1
        elif num < 0:
            return -1
        else:
            return 0

    def resolve_coll(self, pos, vel):
        self.pos, self.vel = pos, vel
