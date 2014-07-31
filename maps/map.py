from xml.etree import ElementTree as ET
from graphics.primitives import Rect
from collision.aabb import AABB
from collision.quadtree import QuadTree
from player.state import vec2


class Map(object):
    """docstring for Map"""
    def __init__(self, mapname, server=False):
        super(Map, self).__init__()
        self.name = mapname
        self.rects = []
        self.quad_tree = None
        self.server = server
        if server:
            self.Rect = AABB
        else:
            self.Rect = Rect
        self.load(''.join(('maps/', mapname, '.svg')))

    def load(self, mapname):
        tree = ET.parse(mapname)
        root = tree.getroot()
        rects = []

        for child in root.getchildren():
            if child.attrib['id'] == 'layer1':
                for rect in child:
                    atr = rect.attrib
                    x = int(atr['x'])
                    y = int(atr['y'])
                    width = int(atr['width'])
                    height = int(atr['height'])
                    color = (1, 1, 1)
                    rects.append(self.Rect(x, - y - height, width,
                                 height, color))

        max_x = max(rect.pos.x + rect.width for rect in rects)
        max_y = max(rect.pos.y + rect.height for rect in rects)

        self.quad_tree = QuadTree(0, self.Rect(0, 0, max_x, max_y),
                                  server=self.server)
        self.rects = rects
        self.quad_tree.clear()
        for rect in rects:
            self.quad_tree.insert(rect)

        self.spawns = []
        for child in root.getchildren():
            if child.attrib['id'] == 'layer2':
                for recht in child:
                    atr = recht.attrib
                    x = int(atr['x'])
                    y = int(atr['y'])
                    height = int(atr['height'])
                    self.spawns.append(vec2(x, -y - height))

    def draw(self):
        for rect in self.rects:
            rect.draw()
