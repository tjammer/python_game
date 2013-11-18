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

    def update(self):
        self.x2 = self.x + self.width
        self.ver_list.vertices = [self.x, self.y, self.x, self.y2,
                                  self.x2, self.y2, self.x2, self.y]
