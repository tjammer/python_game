from xml.etree import ElementTree as ET
from graphics.primitives import Rect


class Map(object):
    """docstring for Map"""
    def __init__(self, mapname):
        super(Map, self).__init__()
        self.rects = []
        self.load(''.join(('maps/', mapname, '.svg')))

    def load(self, mapname):
        tree = ET.parse(mapname)
        root = tree.getroot()

        for rect in root.getchildren()[-1]:
            atr = rect.attrib
            x = int(atr['x'])
            y = int(atr['y'])
            width = int(atr['width'])
            height = int(atr['height'])
            color = (1, 1, 1)
            print y
            self.rects.append(Rect(x, y + height, width, height, color))

    def draw(self):
        for rect in self.rects:
            rect.draw()
