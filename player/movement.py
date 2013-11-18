from pyglet.window import key


class Move(object):
    """docstring for Move"""
    def __init__(self):
        super(Move, self).__init__()
        self.pos = [10, 0]
        self.vel = [0, 0]
        self.gravity = 10.
        self.normal_accel = 10.
        self.boost_accel = 20.
        self.turn_multplier = 2.

        def step(self, dt):
            self.vel[1] += self.gravity
            for i, j in enumerate(self.pos):
                self.pos[i] += self.vel[i] * dt

    def walk(self, sign, dt):
        if sign == 0:
            return False

        curr_sign = self.sign_of(self.vel[0])
        v = self.normal_accel
        if curr_sign != 0 and curr_sign != sign:
            v *= self.turn_multplier
        self.vel[0] += v * sign * dt

    def sign_of(self, num):
        if num > 0:
            return 1
        elif num < 0:
            return -1
        else:
            return 0

    def receive_message(self, event, msg):
        pass
