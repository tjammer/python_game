

class Move(object):
    """docstring for Move"""
    def __init__(self):
        super(Move, self).__init__()
        self.pos = [0, 0]
        self.vel = [0, 0]
        self.gravity = 4000.
        self.normal_accel = 500.
        self.boost_accel = 20.
        self.turn_multplier = 4.
        self.jump_vel = 1500.
        self.can_jump = True
        self.max_vel = 500

        self.input = {}

    def update(self, dt):
        if self.vel[1] == 0:
            self.ground_control(dt)
        else:
            self.air_control(dt)
        if self.vel[1] == 0:
            self.can_jump = True
        self.step(dt)
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.vel[1] = 0
        return self.vel, self.pos

    def step(self, dt):
            self.vel[1] -= self.gravity * dt
            for i, j in enumerate(self.pos):
                self.pos[i] += self.vel[i] * dt

    def walk(self, dt):
        if self.input['right'] and not self.input['left']:
            sign = 1
        elif self.input['left'] and not self.input['right']:
            sign = -1
        else:
            return False

        self.curr_sign = self.sign_of(self.vel[0])
        v = self.normal_accel
        if self.curr_sign != 0 and self.curr_sign != sign:
            v *= self.turn_multplier
        self.vel[0] += v * sign * dt
        if abs(self.vel[0]) > self.max_vel:
            self.vel[0] = self.max_vel * self.curr_sign
        return True

    def air_control(self, dt):
        if not self.input['up'] and self.vel[1] > 0:
            self.vel[1] = 0

        self.walk(dt)

    def ground_control(self, dt):
        if self.input['up'] and self.can_jump:
            self.vel[1] = self.jump_vel
            self.can_jump = False
            return

        if not self.walk(dt):
            self.vel[0] = 0

    def sign_of(self, num):
        if num > 0:
            return 1
        elif num < 0:
            return -1
        else:
            return 0

    def resolve_coll(self, pos, vel):
        self.pos = pos
        self.vel = vel
