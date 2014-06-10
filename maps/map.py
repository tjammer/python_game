from xml.etree import ElementTree as ET
from graphics.primitives import Rect
from collision.rectangle import Rectangle
from collision.quadtree import QuadTree


class Map(object):
    """docstring for Map"""
    def __init__(self, mapname, server=False):
        super(Map, self).__init__()
        self.name = mapname
        self.rects = []
        self.quad_tree = None
        self.server = server
        if server:
            self.Rect = Rectangle
        else:
            self.Rect = Rect
        self.load(''.join(('maps/', mapname, '.svg')))

    def load(self, mapname):
        tree = ET.parse(mapname)
        root = tree.getroot()
        rects = []

        for rect in root.getchildren()[-1]:
            atr = rect.attrib
            x = int(atr['x'])
            y = int(atr['y'])
            width = int(atr['width'])
            height = int(atr['height'])
            color = (1, 1, 1)
            rects.append(self.Rect(x, y + height, width, height, color))

        max_x = max(rect.x1 + rect.width for rect in rects)
        max_y = max(rect.y1 + rect.height for rect in rects)

        self.quad_tree = QuadTree(0, self.Rect(0, 0, max_x, max_y))
        self.rects = rects
        self.quad_tree.clear()
        for rect in rects:
            self.quad_tree.insert(rect)

    def draw(self):
        for rect in self.rects:
            rect.draw()
