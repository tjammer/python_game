from pyglet import graphics
from pyglet import gl
from collision.aabb import AABB, Line, vec2

font = 'Helvetica'


class Rect(AABB):
    """docstring for Rect"""
    def __init__(self, x, y, width, height, color=(255, 255, 255),
                 isplayer=False, batch=None, **kwargs):
        super(Rect, self).__init__(x, y, width, height, color)
        if not batch:
            self.ver_list = graphics.vertex_list(4,
                ('v2f/stream', (x, y, x, y + height,
                 x + width, y + height, x + width, y)),
                ('c3B', (self.color[0], self.color[1], self.color[2],
                 self.color[0], self.color[1], self.color[2],
                 self.color[0], self.color[1], self.color[2],
                 self.color[0], self.color[1], self.color[2])))
        else:
            self.ver_list = batch.add(4, gl.GL_QUADS, None,
                                     ('v2f/stream', (x, y, x, y + height,
                                      x + width, y + height, x + width, y)),
                                     ('c3B', [self.color[0],
                                              self.color[1],
                                              self.color[2]] * 4))
        self.isplayer = isplayer

    def draw(self):
        self.ver_list.draw(gl.GL_QUADS)

    def on_update(self, x, y):
        self.ver_list.vertices = [self.pos.x, self.pos.y, self.pos.x,
                                  self.pos.y + self.height,
                                  self.pos.x + self.width,
                                  self.pos.y + self.height,
                                  self.pos.x + self.width, self.pos.y]

    def update_color(self, color):
        self.ver_list.colors = list(color) * 4
        self.color = color

    def remove(self):
        self.ver_list.delete()

    def delete(self):
        self.remove()

    def add(self, batch):
        self.ver_list = batch.add(4, gl.GL_QUADS, None,
                                 ('v2f/stream', (self.pos.x, self.pos.y,
                                  self.pos.x, self.pos.y + self.height,
                                  self.pos.x + self.width,
                                  self.pos.y + self.height,
                                  self.pos.x + self.width, self.pos.y)),
                                  ('c3B', [self.color[0], self.color[1],
                                   self.color[2]] * 4))

    def copy(self):
        rct = Rect(x=self.pos.x, y=self.pos.y, height=self.height,
                   width=self.width, isplayer=self.isplayer, color=self.color)
        rct.vel = vec2(*self.vel)
        return rct


class DrawaAbleLine(Line):
    """docstring for DrawaAbleLine"""
    def __init__(self, x, y, dx, dy, length=0, batch=None, color=(255, 255, 0),
                 **kwargs):
        super(DrawaAbleLine, self).__init__(x, y, dx, dy, length)
        if length == 0:
            self.length = 1000
        else:
            self.length = length
        if not batch:
            self.ver_list = graphics.vertex_list(2,
                                                 ('v2f/stream', (x, y,
                                                  x + dx * self.length,
                                                  y + dy * self.length)),
                                                 ('c3B', color * 2))
        else:
            self.ver_list = batch.add(2, gl.GL_LINES, None,
                                      ('v2f/stream', (x, y,
                                       x + self.unit.x * self.length,
                                       y + self.unit.y * self.length)),
                                      ('c3B', color * 2))

    def on_update(self):
        self.ver_list.vertices = [self.pos.x, self.pos.y,
                                  self.pos.x + self.unit.x * self.length,
                                  self.pos.y + self.unit.y * self.length]

    def draw(self):
        self.ver_list.draw(gl.GL_LINES)

    def update_color(self, color):
        self.ver_list.colors = list(color) * 2

    def remove(self):
        self.ver_list.delete()

    def add(self, batch):
        self.ver_list = batch.add(2, gl.GL_LINES, None,
                                  ('v2f/stream', (self.pos.x, self.pos.y,
                                   self.pos.x + self.unit.x * self.length,
                                   self.pos.y + self.unit.y * self.length)),
                                  ('c3B', self.color * 2))


class Triangle(object):
    """docstring for Triangle"""
    def __init__(self, x, y, width, height, color, batch, ind, keystr):
        super(Triangle, self).__init__()
        self.ind = ind
        self.x, self.y, self.width, self.height = x, y, width, height
        self.color = color
        self.keystr = keystr
        self.ver_list = batch.add(3, gl.GL_TRIANGLES, None,
                                  ('v2f', (self.x, self.y, self.x + self.width,
                                   self.y, self.x + self.width / 2,
                                   self.y + self.height)),
                                  ('c3B', self.color * 3))

    def add(self, batch):
        self.ver_list = batch.add(3, gl.GL_TRIANGLES, None,
                                  ('v2f', (self.x, self.y, self.x + self.width,
                                   self.y, self.x + self.width / 2,
                                   self.y + self.height)),
                                  ('c3B', self.color * 3))

    def remove(self):
        if len(self.ver_list.get_domain() .allocator.sizes):
            self.ver_list.delete()


class AmmoTriangle(Triangle):
    """docstring for AmmoTriangle"""
    def __init__(self, x, y, width, height, color, batch, ind, keystr, f_s=3):
        super(AmmoTriangle, self).__init__(x, y, width, height, color, batch,
                                           ind, keystr)
        self.fs = f_s
        self.ver_list.delete()
        self.ver_list = batch.add(6, gl.GL_LINES, None,
                                  ('v2f', (self.x, self.y, self.x + self.width,
                                   self.y, self.x + self.width / 2,
                                   self.y + self.height, self.x + self.width,
                                   self.y, self.x + self.width / 2,
                                   self.y + self.height, self.x, self.y)),
                                  ('c3B', self.color * 6))

    def add(self, batch):
        self.ver_list = batch.add(6, gl.GL_LINES, None,
                                  ('v2f', (self.x, self.y, self.x + self.width,
                                   self.y, self.x + self.width / 2,
                                   self.y + self.height, self.x + self.width,
                                   self.y, self.x + self.width / 2,
                                   self.y + self.height, self.x, self.y)),
                                  ('c3B', self.color * 6))

    def remove(self):
        self.ver_list.delete()
        #self.inner.delete()


class HealthBox(object):
    """docstring for HealthBox"""
    def __init__(self, x, y, width, height, color, batch, ind):
        super(HealthBox, self).__init__()
        self.ind = ind
        self.x, self.y, self.width, self.height = x, y, width, height
        self.x = self.x + self.width / 2
        self.color = color
        self.a = self.width / 2**(0.5)
        self.ver_list = batch.add(4, gl.GL_QUADS, None,
                                  ('v2f', (self.x, self.y,
                                   self.x + self.a, self.y + self.a,
                                   self.x, self.y + 2 * self.a,
                                   self.x - self.a, self.y + self.a)),
                                  ('c3B', self.color * 4))

    def add(self, batch):
        self.ver_list = batch.add(4, gl.GL_QUADS, None,
                                  ('v2f', (self.x, self.y,
                                   self.x + self.a, self.y + self.a,
                                   self.x, self.y + 2 * self.a,
                                   self.x - self.a, self.y + self.a)),
                                  ('c3B', self.color * 4))

    def remove(self):
        self.ver_list.delete()


class DrawableArmor(Rect):
    """docstring for DrawableArmor"""
    def __init__(self, value, bonus, respawn, ind, *args, **kwargs):
        super(DrawableArmor, self).__init__(*args, **kwargs)
        self.inactive = False
        self.value = value
        self.bonus = bonus
        self.respawn = respawn
        self.ind = ind


class DrawableTeleporter(object):
    """docstring for DrawableTeleporter"""
    def __init__(self, x, y, width, height, color, batch):
        super(DrawableTeleporter, self).__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.ver_list = batch.add(6, gl.GL_TRIANGLES, None,
                                  ('v2f', (self.x, self.y,
                                   self.x + self.width, self.y,
                                   self.x+self.width/2, self.y+self.height/2,
                                   self.x+self.width/2, self.y+self.height/2,
                                   self.x + self.width, self.y + self.height,
                                   self.x, self.y + self.height)),
                                  ('c3B', self.color * 6))

    def add(self, batch):
        self.ver_list = batch.add(6, gl.GL_TRIANGLES, None,
                                  ('v2f', (self.x, self.y,
                                   self.x + self.width, self.y,
                                   self.x+self.width/2, self.y+self.height/2,
                                   self.x+self.width/2, self.y+self.height/2,
                                   self.x + self.width, self.y + self.height,
                                   self.x, self.y + self.height)),
                                  ('c3B', self.color * 6))

    def remove(self):
        self.ver_list.remove()


class CrossHair(object):
    """docstring for CrossHair"""
    def __init__(self, batch, pos=[0, 0], size=10):
        super(CrossHair, self).__init__()
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.size = size
        self.cross = batch.add(4, gl.GL_LINES, None,
                               ('v2f/stream', (self.x - self.size,
                                self.y, self.x + self.size, self.y,
                                self.x, self.y - self.size,
                                self.x, self.y + self.size)),
                               ('c3B', [255] * 12))
        self.drawable = True

    def update(self, x, y):
        self.x = x
        self.y = y
        self.cross.vertices = (self.x - self.size, self.y, self.x + self.size,
                               self.y, self.x, self.y - self.size, self.x,
                               self.y + self.size)

    def draw(self, x, y):
        self.update(x, y)
        gl.glColor3f(1, 1, 1)
        self.cross.draw(gl.GL_LINES)

    def remove(self):
        if len(self.cross.get_domain() .allocator.sizes):
            self.cross.delete()

    def add(self, batch):
        if not len(self.cross.get_domain() .allocator.sizes):
            self.cross = batch.add(4, gl.GL_LINES, None,
                                   ('v2f/stream', (self.x - self.size,
                                    self.y, self.x + self.size, self.y,
                                    self.x, self.y - self.size,
                                    self.x, self.y + self.size)),
                                   ('c3B', [255] * 12))


class Box(object):
    """docstring for Box"""
    def __init__(self, pos, size, f_size=2, color=(0, 255, 255),
                 hcolor=(255, 255, 0), batch=None, innercol=(0, 0, 0)):
        super(Box, self).__init__()
        self.pos = pos
        self.width = size[0]
        self.height = size[1]
        self.f_size = f_size
        self.color = color
        self.h_color = hcolor
        self.outer_box = Rect(pos[0], pos[1], self.width, self.height,
                              self.color,
                              batch=batch)
        self.inner_box = Rect(pos[0] + f_size, pos[1] + f_size,
                              self.width - 2 * f_size,
                              self.height - 2 * f_size,
                              innercol, batch=batch)

    def draw(self):
        self.outer_box.draw()
        self.inner_box.draw()

    def highlight(self):
        self.outer_box.ver_list.colors = list(self.h_color) * 4

    def restore(self):
        self.outer_box.ver_list.colors = list(self.color) * 4

    def update(self):
        self.outer_box.update(*self.pos)
        self.inner_box.update(self.pos[0] + self.f_size,
                              self.pos[1] + self.f_size)

    def new_size(self, width, height):
        self.outer_box.width = width
        self.outer_box.height = height
        self.inner_box.width = width - 2 * self.f_size
        self.inner_box.height = height - 2 * self.f_size
