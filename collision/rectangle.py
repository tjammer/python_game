import math
import vector

pi = math.acos(0) * 2


class Rectangle(object):
    """points for Rectangle are clockwise, starting with left-bottom"""
    def __init__(self, x, y, width, height, color=(1., 1., 1.), angle=0):
        super(Rectangle, self).__init__()
        self.width = width
        self.height = height
        self.angle = angle * pi / 180

        self.x1, self.y1 = x, y
        self.x2, self.y2 = self.rotated_coord(0, self.height)
        self.x3, self.y3 = self.rotated_coord(self.width, self.height)
        self.x4, self.y4 = self.rotated_coord(self.width, 0)
        self.color = color

        self.axis1x, self.axis1y = self.rotate(1, 0)
        self.axis2x, self.axis2y = self.rotate(0, 1)

    def update(self, x, y):
        self.x1, self.y1 = x, y
        self.x2, self.y2 = self.rotated_coord(0, self.height)
        self.x3, self.y3 = self.rotated_coord(self.width, self.height)
        self.x4, self.y4 = self.rotated_coord(self.width, 0)

    def collides(self, rect):
        return vector.collides(self, rect)

    def rotate(self, x, y):
        x_ = x * math.cos(self.angle) - y * math.sin(self.angle)
        y_ = x * math.sin(self.angle) + y * math.cos(self.angle)
        return x_, y_

    def rotated_coord(self, x, y):
        x_, y_ = self.rotate(x, y)
        return self.x1 + x_, self.y1 + y_
