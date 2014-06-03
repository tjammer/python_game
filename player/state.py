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


class state(object):
    """docstring for state"""
    def __init__(self, pos, vel, hp=100):
        super(state, self).__init__()
        self.pos, self.vel, self.hp = pos, vel, hp
