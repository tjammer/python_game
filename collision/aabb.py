from player.state import vec2


class AABB(object):
    """docstring for AABB"""
    def __init__(self, x, y, width, height, color=(1., 1., 1.),
                 isplayer=False):
        super(AABB, self).__init__()
        self.pos = vec2(x, y)
        self.vel = vec2(0, 0)
        self.width = width
        self.height = height
        self.hwidth = width / 2.
        self.hheight = height / 2.
        self.center = vec2(self.pos.x + self.hwidth, self.pos.y + self.hheight)
        self.color = color
        self.isplayer = isplayer

    def update(self, x, y):
        self.pos = vec2(x, y)
        self.center = vec2(self.pos.x + self.hwidth, self.pos.y + self.hheight)
        self.on_update(x, y)

    def on_update(self, x, y):
        pass

    def overlaps(self, aabb):
        distance = (self.center - aabb.center)
        xovr = abs(distance.x) - self.hwidth - aabb.hwidth
        if xovr < 0:
            yovr = abs(distance.y) - self.hheight - aabb.hheight
            if yovr < 0:
                return xovr, yovr
        return False

    def collides(self, aabb):
        return self.overlaps(aabb)

    def sweep(self, obj, dt):
        ovrtest = self.overlaps(obj)
        if ovrtest:
            x, y = ovrtest
            norm = vec2(float(x > y), -float(y > x))
            if not obj.isplayer:
                return norm, -dt
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
                if xdist_ent * xdist_ext > 0:
                    return False
            else:
                xt_ent = xdist_ent / self.vel.x
                xt_ext = xdist_ext / self.vel.x
            if self.vel.y == 0:
                yt_ent = -float('Inf')
                yt_ext = float('Inf')
                if ydist_ent * ydist_ext > 0:
                    return False
            else:
                yt_ent = ydist_ent / self.vel.y
                yt_ext = ydist_ext / self.vel.y
            enter = max(xt_ent, yt_ent)
            exit = min(xt_ext, yt_ext)
            #no coll
            if enter > exit or (xt_ent < 0
                                and yt_ent < 0) or xt_ent > dt or yt_ent > dt:
                return False
            #normal
            if xt_ent > yt_ent:
                if xdist_ent >= 0 and self.vel.x > 0 and yt_ent != 0:
                    normal = vec2(1., 0.)
                elif xdist_ent <= 0 and self.vel.x < 0 and yt_ent != 0:
                    normal = vec2(-1., 0.)
                else:
                    return False
            else:
                if ydist_ent <= 0:
                    normal = vec2(0., -1.)
                else:
                    normal = vec2(0., 1.)
            return normal, enter, dt - enter

    def sign_of(self, vec):
        if not isinstance(vec, vec2):
            if vec == 0:
                return 0
            else:
                return vec / abs(vec)
        else:
            return vec2(self.sign_of(vec.x), self.sign_of(vec.y))


class Line(object):
    """line is in principle aabb with width = 0"""
    def __init__(self, x, y, dx, dy, length=0, color=(255, 255, 255)):
        super(Line, self).__init__()
        self.pos = vec2(x, y)
        self.dir = vec2(dx, dy)
        self.unit = self.dir / self.dir.mag()
        if length == 0:
            self.length = float('Inf')
        else:
            self.length = length

    def sweep(self, obj):
        if self.dir.x > 0:
            xdist_ent = obj.pos.x - self.pos.x
            xdist_ext = obj.pos.x + obj.width - self.pos.x
        else:
            xdist_ent = obj.pos.x + obj.width - self.pos.x
            xdist_ext = obj.pos.x - self.pos.x
        if self.dir.y > 0:
            ydist_ent = obj.pos.y - self.pos.y
            ydist_ext = obj.pos.y + obj.height - self.pos.y
        else:
            ydist_ent = obj.pos.y + obj.height - self.pos.y
            ydist_ext = obj.pos.y - self.pos.y
        #find time for entry and exit
        xt_ent = xdist_ent / self.unit.x
        xt_ext = xdist_ext / self.unit.x

        yt_ent = ydist_ent / self.unit.y
        yt_ext = ydist_ext / self.unit.y

        enter = max(xt_ent, yt_ent)
        exit = min(xt_ext, yt_ext)

        if enter > exit or (enter < 0 and exit < 0) or enter > self.length:
            return False

        return enter, exit

    def collide(self, quadtree, playergen, id):
        mapcolls = []
        rect = AABB(*self.pos, width=0, height=0)
        bnd = quadtree.retrieve_bound(rect)
        while len(mapcolls) == 0:
            mapgen = (rect_ for rect_ in quadtree.retrieve([], rect))
            for rct in mapgen:
                #print rct.pos.x
                response = self.sweep(rct)
                if response:
                    enter, exit = response
                    mapcolls.append(enter)
            if len(mapcolls) == 0:
                #bound = quadtree.retrieve_bound(rect)
                try:
                    enter, exit = self.sweep(bnd)
                except TypeError:
                    break
                rect.pos += self.unit * (exit + 1)
                bound = quadtree.retrieve_bound(rect)
                if bound.pos.x == bnd.pos.x:
                    break
                bnd = bound
        if mapcolls:
            mapcoll = min(mapcolls)
        else:
            mapcoll = float('Inf')
        p_response = [self.sweep(pl.rect) for pl in playergen if pl.id != id]
        try:
            playercoll = min((p for p in p_response if p is not False))
        except ValueError:
            playercoll = float('Inf')
        coll = min(mapcoll, playercoll)
        if coll == float('Inf'):
            return False
        elif mapcoll < playercoll:
            return mapcoll, False
        else:
            return playercoll, True

    def update(self, x, y, mx, my):
        dx = mx - x
        dy = my - y
        self.pos.x, self.pos.y = x, y
        self.dir.x, self.dir.y = dx, dy
        self.unit = self.dir / self.dir.mag()
        self.on_update()
