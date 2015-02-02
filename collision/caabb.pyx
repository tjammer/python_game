from player.cvec2 cimport cvec2
cimport cython
from libc.math cimport copysign

cdef class cAABB:
    cdef public cvec2 pos, vel, center
    cdef public float width, height, hwidth, hheight
    cdef public object color, isplayer

    def __init__(self, float x=0, float y=0, float width=0, float height=0,
                 color=(1., 1., 1.), isplayer=False, batch=None):
        self.pos = cvec2(x, y)
        self.vel = cvec2(0, 0)
        self.width = width
        self.height = height
        self.hwidth = width / 2.
        self.hheight = height / 2.
        self.center = cvec2(self.pos.x + self.hwidth, self.pos.y + self.hheight)
        self.color = color
        self.isplayer = isplayer

    def __richcmp__(self, cAABB other, int op):
        if op == 2:
            if other.pos == self.pos:
                if other.center == self.center:
                    return True
            return False
        elif op == 3:
            if other.pos == self.pos:
                if other.center == self.center:
                    return False
            return True
        else:
            raise TypeError

    def update(self, float x, float y):
        self.pos.x, self.pos.y = x, y
        self.center.x = self.pos.x + self.hwidth
        self.center.y = self.pos.y + self.hheight
        self.on_update(x, y)

    def on_update(self, float x, float y):
        pass

    def overlaps(self, cAABB aabb):
        cdef float distancey, yovr
        cdef float distancex = self.center.x - aabb.center.x
        cdef float xovr = abs(distancex) - self.hwidth - aabb.hwidth
        if xovr < 0:
            distancey = self.center.y - aabb.center.y
            yovr = abs(distancey) - self.hheight - aabb.hheight
            if yovr < 0:
                return xovr, yovr
        return False

    def collides(self, aabb):
        return self.overlaps(aabb)

    @cython.cdivision(True)
    def sweep(self, cAABB obj, float dt):
        ovrtest = self.overlaps(obj)
        if ovrtest:
            x, y = ovrtest
            norm = cvec2(float(x > y), -float(y > x))
            if not obj.isplayer:
                return norm, -dt, dt
            elif not self.isplayer:
                return norm, dt, dt
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
            if -0.0001 < self.vel.x < 0.0001:
                xt_ent = -float('Inf')
                xt_ext = float('Inf')
                if xdist_ent * xdist_ext >= 0:
                    return False
            else:
                xt_ent = xdist_ent / self.vel.x
                xt_ext = xdist_ext / self.vel.x
            if -0.0001 < self.vel.y < 0.0001:
                yt_ent = -float('Inf')
                yt_ext = float('Inf')
                if ydist_ent * ydist_ext >= 0:
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
                    normal = cvec2(1., 0.)
                elif xdist_ent <= 0 and self.vel.x < 0 and yt_ent != 0:
                    normal = cvec2(-1., 0.)
                else:
                    normal = cvec2(copysign(1., self.vel.x), 0.)
            else:
                if ydist_ent < 0:
                    normal = cvec2(0., -1.)
                elif ydist_ent > 0:
                    normal = cvec2(0., 1.)
                else:
                    normal = cvec2(0., copysign(1., self.vel.y))
            # return normal, enter, dt - enter
            return normal, enter, min(xt_ent, yt_ent)

    def sign_of(self, vec):
        if not isinstance(vec, cvec2):
            if vec == 0:
                return 0
            else:
                return vec / abs(vec)
        else:
            return cvec2(self.sign_of(vec.x), self.sign_of(vec.y))

    def copy(self):
        rct = cAABB(x=self.pos.x, y=self.pos.y, height=self.height,
                   width=self.width, isplayer=self.isplayer, color=self.color)
        rct.vel = cvec2(*self.vel)
        return rct


cdef class Line:
    """line is in principle aabb with width = 0"""
    cdef public cvec2 pos, dir, unit
    cdef public float length
    def __init__(self, x, y, dx, dy, length=0):
        super(Line, self).__init__()
        self.pos = cvec2(x, y)
        self.dir = cvec2(dx, dy)
        self.unit = self.dir.normalize()
        if length == 0:
            self.length = float('Inf')
        else:
            self.length = length

    def sweep(self, cAABB obj):
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
        try:
            xt_ent = xdist_ent / self.unit.x
            xt_ext = xdist_ext / self.unit.x
        except ZeroDivisionError:
            xt_ent = -float('Inf')
            xt_ext = float('Inf')

        try:
            yt_ent = ydist_ent / self.unit.y
            yt_ext = ydist_ext / self.unit.y
        except ZeroDivisionError:
            yt_ent = -float('Inf')
            yt_ext = float('Inf')

        enter = max(xt_ent, yt_ent)
        exit = min(xt_ext, yt_ext)

        if enter > exit or (enter < 0 and exit < 0) or enter > self.length:
            return False

        return enter, exit

    def collide(self, quadtree, playergen, int id):
        mapcolls = []
        cdef cAABB bnd, rect
        rect = cAABB(*self.pos, width=0, height=0)
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
                if bound == bnd:
                    break
                bnd = bound
        if mapcolls:
            mapcoll = min(mapcolls)
        else:
            mapcoll = float('Inf')
        p_resp = [(self.sweep(pl.rect), pl.id)
                  for pl in playergen if pl.id != id]
        try:
            playercoll = min((p[0][0] for p in p_resp if p[0] is not False))
        except ValueError:
            playercoll = float('Inf')
        coll = min(mapcoll, playercoll)
        if coll == float('Inf'):
            return False
        elif mapcoll < playercoll:
            return mapcoll, False
        else:
            return playercoll, [r[1]
                                for r in p_resp if r[0][0] == playercoll][0]

    def update(self, float x, float y, float mx, float my):
        cdef float dx, dy
        dx = mx - x
        dy = my - y
        self.pos.x, self.pos.y = x, y
        self.dir.x, self.dir.y = dx, dy
        self.unit = self.dir.normalize()
        self.on_update()
