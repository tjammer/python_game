from xml.etree import ElementTree as ET
from graphics.primitives import Rect
from collision.aabb import AABB
from collision.quadtree import QuadTree
from player.state import vec2
from gameplay.items import Armor, DrawableArmor, ItemManager
from gameplay.items import armors


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
            self.Armor = Armor
        else:
            self.Rect = Rect
            self.Armor = DrawableArmor
        self.items = ItemManager()
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

        #armors
        self.ind = 0
        for child in root.getchildren():
            if child.attrib['id'] == 'layer3':
                for rect in child:
                    atr = rect.attrib
                    x = int(atr['x'])
                    y = int(atr['y'])
                    width = int(atr['width'])
                    height = int(atr['height'])
                    avalue = int(atr['armor'])
                    color, maxarmor = armors[avalue]
                    armor = self.Armor(x=x, y=-y-height, width=width,
                                       height=height, value=avalue,
                                       bonus=False, respawn=10, color=color,
                                       ind=self.ind, maxarmor=maxarmor)
                    self.items.add(armor)
                    self.ind += 1

    def draw(self):
        for rect in self.rects:
            rect.draw()
        for item in self.items:
            item.draw()

    def serverupdate(self, itemid, spawn):
        self.items.fromserver(itemid, spawn)
