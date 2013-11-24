from pyglet import graphics
from pyglet import gl


class Rect(object):
    """Rectangle Class"""
    def __init__(self, x, y, width, height, color):
        super(Rect, self).__init__()
        # Position of Rect, x,y from lower left
        self.x = x
        self.y = y
        self.x2 = x + width
        self.y2 = y + height
        self.width = width
        self.height = height
        self.color = color
        self.ver_list = graphics.vertex_list(4,
                    ('v2f', (self.x, self.y, self.x, self.y2,
                             self.x2, self.y2, self.x2, self.y)),
                    ('c3f', (self.color[0], self.color[1], self.color[2],
                     self.color[0], self.color[1], self.color[2],
                     self.color[0], self.color[1], self.color[2],
                     self.color[0], self.color[1], self.color[2])))

    def draw(self):
        self.ver_list.draw(gl.GL_POLYGON)

    def update(self, x, y):
        self.x = x
        self.y = y
        self.x2 = x + self.width
        self.y2 = y + self.height
        self.ver_list.vertices = [self.x, self.y, self.x, self.y2,
                                  self.x2, self.y2, self.x2, self.y]


class Cross(object):
    """docstring for Cross"""
    def __init__(self, pos, size):
        super(Cross, self).__init__()
        self.size = size
        self.pos = pos
        self.h_line = Rect(pos[0] - size / 2., pos[1], size, 2, (1, 1, 1))
        self.v_line = Rect(pos[0], pos[1] + size / 2, 2, size, (1, 1, 1))

    def draw(self):
        self.h_line.draw()
        self.v_line.draw()

    def update(self, x, y):
        self.h_line.update(x - self.size / 2, y - 1)
        self.v_line.update(x - 1, y - self.size / 2)


class Box(object):
    """docstring for Box"""
    def __init__(self, pos, size, f_size):
        super(Box, self).__init__()
        self.pos = pos
        self.size = size
        self.f_size = f_size
        self.outer_box = Rect(pos[0], pos[1], size[0], size[1], (.1, .8, 0))
        self.inner_box = Rect(pos[0] + f_size, pos[1] + f_size,
                              size[0] - 2 * f_size, size[1] - 2 * f_size,
                              (0, 0, 0))

    def draw(self):
        self.outer_box.draw()
        self.inner_box.draw()

    def highlight(self):
        self.outer_box.ver_list.colors = [1, 0, 0]

    def restore(self):
        self.outer_box.ver_list.colors = [0, 1, 0]
