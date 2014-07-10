from math import sqrt
from network_utils import protocol_pb2 as proto


class vec2(object):
    """docstring for vec2"""
    def __init__(self, x, y):
        super(vec2, self).__init__()
        self.x, self.y = x, y

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    def __repr__(self):
        return ', '.join((str(self.x), str(self.y)))

    def __sub__(self, vec):
        if isinstance(vec, vec2):
            return vec2(self.x - vec.x, self.y - vec.y)
        else:
            raise TypeError

    def __add__(self, vec):
        if isinstance(vec, vec2):
            return vec2(self.x + vec.x, self.y + vec.y)
        else:
            raise TypeError

    def __mul__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return vec2(self.x * num, self.y * num)
        elif isinstance(num, vec2):
            return vec2(self.x * num.x, self.y * num.y)

    def __div__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return vec2(self.x / num, self.y / num)
        else:
            raise TypeError

    def mag(self):
        """magnitude of the vector"""
        return sqrt(self.x**2 + self.y**2)


class state(object):
    """docstring for state"""
    def __init__(self, pos, vel, hp=100, conds=False):
        super(state, self).__init__()
        self.pos, self.vel, self.hp = pos, vel, hp
        self.wall_t = .2
        self.wall = 0
        if not conds:
            self.conds = proto.MState()
            self.conds.canJump = True
        else:
            self.conds = conds

    def set_cond(self, condname):
        if condname == 'ascending':
            self.conds.ascending = True
            self.conds.onGround = False
            self.conds.landing = False
            self.conds.canJump = False
            self.conds.onRightWall = False
            self.conds.onLeftWall = False
            self.conds.descending = False
        elif condname == 'canJump':
            self.conds.canJump = True
        elif condname == 'onGround':
            if not self.conds.onGround:
                if not self.conds.landing:
                    self.conds.landing = True
                    self.conds.descending = False
                    self.conds.ascending = False
                else:
                    self.conds.onGround = True
                    self.conds.landing = False
        elif condname == 'descending':
            self.conds.ascending = False
            self.conds.descending = True
            self.conds.onRightWall = False
            self.conds.onLeftWall = False
            self.conds.onGround = False
            self.conds.landing = False
        elif condname == 'onRightWall':
            self.conds.onRightWall = True
            self.conds.ascending = False
            self.conds.descending = False
            self.wall = self.wall_t
        elif condname == 'onLeftWall':
            self.conds.onLeftWall = True
            self.conds.ascending = False
            self.conds.descending = False
            self.wall = self.wall_t

    def update(self, dt):
        self.wall -= dt
        if self.wall < 0:
            self.wall = 0
            self.conds.onRightWall = False
            self.conds.onLeftWall = False

    def copy(self):
        return state(vec2(*self.pos), vec2(*self.vel), self.hp, self.conds)
