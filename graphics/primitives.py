from pyglet import graphics
from pyglet import gl
from collision.rectangle import Rectangle
from collision.aabb import AABB


class Rect(AABB):
    """docstring for Rect"""
    def __init__(self, x, y, width, height, color=(255, 255, 255),
                 isplayer=False, batch=None, **kwargs):
        super(Rect, self).__init__(x, y, width, height, color)
        self.ver_list = graphics.vertex_list(4,
            ('v2f/stream', (x, y, x, y + height,
             x + width, y + height, x + width, y)),
            ('c3B', (self.color[0], self.color[1], self.color[2],
             self.color[0], self.color[1], self.color[2],
             self.color[0], self.color[1], self.color[2],
             self.color[0], self.color[1], self.color[2])))
        self.isplayer = isplayer
        if batch:
            self.ver_list = batch.add(4, gl.GL_QUADS, None,
                                     ('v2f/stream', (x, y, x, y + height,
                                      x + width, y + height, x + width, y)),
                                     ('c3B', [self.color[0],
                                              self.color[1],
                                              self.color[2]] * 4))

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


class Rect_(Rectangle):
    """Rectangle Class"""
    def __init__(self, x, y, width, height, color=(1., 1., 1.), angle=0):
        super(Rect_, self).__init__(x, y, width, height, color, angle)
        self.ver_list = graphics.vertex_list(4,
                    ('v2f/stream', (self.x1, self.y1, self.x2, self.y2,
                                    self.x3, self.y3, self.x4, self.y4)),
                    ('c3f', (self.color[0], self.color[1], self.color[2],
                     self.color[0], self.color[1], self.color[2],
                     self.color[0], self.color[1], self.color[2],
                     self.color[0], self.color[1], self.color[2])))

    def draw(self):
        self.ver_list.draw(gl.GL_POLYGON)

    def update(self, x, y):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = self.rotated_coord(0, self.height)
        self.x3, self.y3 = self.rotated_coord(self.width, self.height)
        self.x4, self.y4 = self.rotated_coord(self.width, 0)
        self.ver_list.vertices = [self.x1, self.y1, self.x2, self.y2,
                                  self.x3, self.y3, self.x4, self.y4]

    def update_color(self, color):
        self.ver_list.colors = list(color) * 4


class CrossHair(object):
    """docstring for CrossHair"""
    def __init__(self, pos=[0, 0], size=10):
        super(CrossHair, self).__init__()
        self.pos = pos
        self.x = pos[0]
        self.y = pos[1]
        self.size = size
        self.cross = graphics.vertex_list(4,
                                         ('v2i/stream', (self.x - self.size,
                                          self.y, self.x + self.size, self.y,
                                          self.x, self.y - self.size,
                                          self.x, self.y + self.size)))
        self.drawable = True

    def update(self, x, y):
        self.x = x
        self.y = y
        self.cross.vertices = (self.x - self.size, self.y, self.x + self.size,
                               self.y, self.x, self.y - self.size, self.x,
                               self.y + self.size)

    def draw(self, x, y):
        self.update(x, y)
        gl.glColor3d(1, 1, 1)
        self.cross.draw(gl.GL_LINES)


class Box(object):
    """docstring for Box"""
    def __init__(self, pos, size, f_size=2, color=(0, 255, 255),
                 hcolor=(255, 255, 0), batch=None):
        super(Box, self).__init__()
        self.pos = pos
        self.size = size
        self.f_size = f_size
        self.color = color
        self.h_color = hcolor
        self.outer_box = Rect(pos[0], pos[1], size[0], size[1], self.color,
                              batch=batch)
        self.inner_box = Rect(pos[0] + f_size, pos[1] + f_size,
                              size[0] - 2 * f_size, size[1] - 2 * f_size,
                              (0, 0, 0), batch=batch)

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
