import math
from state import vec2


class Movement(object):
    """docstring for Movement"""
    def __init__(self, x, y):
        super(Movement, self).__init__()
        self.pos = vec2(x, y)
        self.vel = vec2(0, 0)
        self.gravity = 2500.
        self.normal_accel = 500.
        self.boost_accel = 20.
        self.turn_multplier = 4.
        self.jump_vel = 900.
        self.max_vel = 500
        self.angle = 0
        self.conds = {'can_jump': False, 'on_ground': False}

    def update(self, dt, pos, vel, input):
        self.calc_vel(dt, pos, vel, input)
        self.step(dt, pos, vel)
        self.set_conds()
        return self.vel, self.pos

    def step(self, dt, pos, vel):
        self.vel[1] = vel[1] - self.gravity * dt
        for i, j in enumerate(self.pos):
            self.pos[i] = pos[i] + self.vel[i] * dt

    def calc_vel(self, dt, pos, vel, input):
        #check left right
        if input.right and not input.left:
            sign = 1
        elif input.left and not input.right:
            sign = -1
        else:
            self.vel[0] = 0
            sign = 0
        self.curr_sign = self.sign_of(vel[0])
        v = self.normal_accel
        if self.curr_sign != 0 and self.curr_sign != sign:
            v *= self.turn_multplier
        self.vel[0] = vel[0] + v * sign * dt
        #self.vel[1] = vel[1] + v * math.tan(self.angle) * sign * dt
        if abs(vel[0]) > self.max_vel:
            self.vel[0] = self.max_vel * self.curr_sign
        #check jump
        if self.conds['can_jump'] and input.up:
            self.vel[1] = self.jump_vel
            self.conds['can_jump'] = False
        #in air
        if not input.up and self.vel[1] > 0:
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
