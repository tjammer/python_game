from state import vec2


class Movement(object):
    """docstring for Movement"""
    def __init__(self, x, y):
        super(Movement, self).__init__()
        self.pos = vec2(x, y)
        self.vel = vec2(0, 0)
        self.gravity = 2500.
        self.normal_accel = 1000.
        self.boost_accel = 20.
        self.turn_multplier = 8.
        self.jump_vel = 900.
        self.max_vel = 500.
        self.wall_boost = 650.
        self.angle = 0
        self.friction = 15

    def update(self, dt, state, input):
        pos, vel, conds = state.pos, state.vel, state.conds
        self.compute_vel(dt, pos, vel, input, conds, state)
        return self.step(dt, pos)

    def step(self, dt, pos):
        self.pos = pos + self.vel * dt
        return self.pos, self.vel

    def get_vel(self, dt, state, input):
        vel, conds = state.vel, state.conds
        self.compute_vel(dt, vel, input, conds, state)
        return self.vel

    def compute_vel(self, dt, vel, input, conds, state):
        self.vel = vel
        avel = abs(vel.x)
        if state.isDead:
            self.vel.x -= self.vel.x * dt * self.friction
            sign = 0
        elif input.right and not input.left:
            sign = 1
        elif input.left and not input.right:
            sign = -1
        else:
            if conds.onGround:
                self.vel.x -= self.vel.x * dt * self.friction
            else:
                self.vel.x -= self.vel.x * dt * self.friction / 5.
            sign = 0
        self.curr_sign = self.sign_of(vel.x)
        if vel.x * sign >= self.max_vel or (conds.onRightWall
                                            and sign < 0) or (conds.onLeftWall
                                                              and sign > 0):
            v = 0
        else:
            v = self.normal_accel
        if conds.onGround and self.curr_sign * sign < 0:
            v *= self.turn_multplier
        if conds.onGround and avel > self.max_vel:
            self.vel.x = self.max_vel * self.curr_sign
        self.vel.x = self.vel.x + v * sign * dt
        #wallsliding
        if (conds.onLeftWall or conds.onRightWall) and self.vel.y < 0:
            gravity = self.gravity * .5
        else:
            gravity = self.gravity
        self.vel.y = self.vel.y - gravity * dt

        if not state.isDead:
            if (conds.landing or
                    conds.onGround) and conds.canJump and input.up:
                self.jump(state)
            elif (conds.onRightWall
                  or conds.onLeftWall) and conds.canJump and input.up:
                self.walljump(state, conds)
        if not input.up:
            state.set_cond('canJump')
            if self.vel.y > 0:
                self.vel.y -= self.vel.y * dt * self.friction * 2

    def jump(self, state):
        self.vel.y = self.jump_vel
        state.set_cond('ascending')

    def walljump(self, state, conds):
        self.vel.y += self.jump_vel * 1.5
        if conds.onLeftWall:
            self.vel.x = self.wall_boost
        elif conds.onRightWall:
            self.vel.x = -self.wall_boost
        state.set_cond('ascending')

    def sign_of(self, num):
        if num > 0:
            return 1
        elif num < 0:
            return -1
        else:
            return 0

    def resolve_coll(self, pos, vel):
        self.pos, self.vel = pos, vel
