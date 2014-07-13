from player.state import vec2


class AABB(object):
    """docstring for AABB"""
    def __init__(self, x, y, width, height):
        super(AABB, self).__init__()
        self.pos = vec2(x, y)
        self.vel = vec2(0, 0)
        self.width = width
        self.height = height
        self.hwidth = width / 2.
        self.hheight = height / 2.
        self.center = vec2(self.pos.x + self.hwidth, self.pos.y + self.hheight)

    def update(self, x, y):
        self.pos = vec2(x, y)
        self.center = vec2(self.pos.x + self.hwidth, self.pos.y + self.hheight)
        self.on_update()

    def on_update(self):
        pass

    def overlaps(self, aabb):
        distance = (self.center - aabb.center)
        if not abs(distance.x) >= self.hwidth + aabb.hwidth:
            if not abs(distance.y) >= self.hheight + aabb.hheight:
                return True
        return False

    def collides(self, aabb):
        return self.overlaps(aabb)

    def sweep(self, obj, dt):
        if self.overlaps(obj):
            return True, vec2(0, 0), 0
        else:
            #find distance for entry and exit
            if self.vel.x > 0:
                xdist_ent = obj.pos.x - self.pos.x - self.width
                xdist_ext = obj.pos.x + obj.width - self.pos.x
            else:
                xdist_ent = obj.pos.x + obj.width - self.pos.x
                xdist_ext = obj.pos.x - self.pos.x - self.width
            if self.vel.y > 0:
                ydist_ent = obj.pos.y - self.pos.y - self.height
                ydist_ext = obj.pos.y + obj.height - self.pos.y
            else:
                ydist_ent = obj.pos.y + obj.height - self.pos.y
                ydist_ext = obj.pos.y - self.pos.y - self.height
            #find time for entry and exit
            if self.vel.x == 0:
                xt_ent = -float('Inf')
                xt_ext = float('Inf')
            else:
                xt_ent = xdist_ent / self.vel.x
                xt_ext = xdist_ext / self.vel.x
            if self.vel.y == 0:
                yt_ent = -float('Inf')
                yt_ext = float('Inf')
            else:
                yt_ent = ydist_ent / self.vel.y
                yt_ext = ydist_ext / self.vel.y
            print xt_ent, xt_ext, yt_ent, yt_ext
            enter = max(xt_ent, yt_ent)
            exit = min(xt_ext, yt_ext)
            print enter, exit
            #no coll
            if enter > exit or (xt_ent < 0
                                and yt_ent < 0) or xt_ent > dt or yt_ent > dt:
                return False
            #normal
            if xt_ent > yt_ent:
                if xdist_ent >= 0:
                    normal = vec2(1., 0.)
                else:
                    normal = vec2(-1., 0.)
            else:
                if ydist_ent <= 0:
                    normal = vec2(0., -1.)
                else:
                    normal = vec2(0., 1.)
            return True, normal, enter

    def sign_of(self, vec):
        if not isinstance(vec, vec2):
            if vec == 0:
                return 0
            else:
                return vec / abs(vec)
        else:
            return vec2(self.sign_of(vec.x), self.sign_of(vec.y))
