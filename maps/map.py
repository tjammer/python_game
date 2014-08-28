from xml.etree import ElementTree as ET
from graphics.primitives import *
from collision.aabb import AABB
from collision.quadtree import QuadTree
from player.state import vec2
from gameplay.items import *
from gameplay.weapons import *
from elements import Teleporter


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
            self.batch = None
        else:
            self.Rect = Rect
            from pyglet.graphics import Batch
            self.batch = Batch()
        self.items = ItemManager(self.batch)
        try:
            self.load(''.join(('maps/', mapname, '.svg')))
        except ET.ParseError:
            pass

    def load(self, mapname):
        tree = ET.parse(mapname)
        root = tree.getroot()
        rects = []

        for child in root.getchildren():
            if child.attrib['id'] == 'layer1':
                for rect in child:
                    atr = rect.attrib
                    x = float(atr['x'])
                    y = float(atr['y'])
                    width = float(atr['width'])
                    height = float(atr['height'])
                    color = (255, 255, 255)
                    rects.append(self.Rect(x, - y - height, width,
                                 height, color, batch=self.batch))

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
                    x = float(atr['x'])
                    y = float(atr['y'])
                    height = float(atr['height'])
                    self.spawns.append(vec2(x, -y - height))

        #armors
        self.ind = 0
        for child in root.getchildren():
            if child.attrib['id'] == 'armors':
                for rect in child:
                    atr = rect.attrib
                    x = float(atr['x'])
                    y = float(atr['y'])
                    width = float(atr['width'])
                    height = float(atr['height'])
                    avalue = int(atr['armor'])
                    color, maxarmor = armors[avalue]
                    respawn = timers['armor']
                    if self.server:
                        armor = Armor(x=x, y=-y-height, width=width,
                                      height=height, value=avalue,
                                      bonus=False, respawn=respawn,
                                      color=color, ind=self.ind,
                                      maxarmor=maxarmor, batch=self.batch)
                    else:
                        armor = DrawableArmor(x=x+6, y=-y-height,
                                              width=width-12,
                                              height=height-12, value=avalue,
                                              bonus=False, respawn=respawn,
                                              color=color, ind=self.ind,
                                              maxarmor=maxarmor,
                                              batch=self.batch)
                    self.items.add(armor)
                    self.ind += 1

        #healths
        for child in root.getchildren():
            if child.attrib['id'] == 'health':
                for rect in child:
                    atr = rect.attrib
                    x = float(atr['x'])
                    y = float(atr['y'])
                    width = float(atr['width'])
                    height = float(atr['height'])
                    hvalue = int(atr['health'])
                    color, maxhp = health[hvalue]
                    respawn = timers['health']
                    if self.server:
                        health_ = Health(x=x, y=-y-height, width=width,
                                         height=height, value=hvalue,
                                         bonus=False, respawn=respawn,
                                         color=color, ind=self.ind,
                                         maxhp=maxhp, batch=self.batch)
                    else:
                        health_ = HealthBox(x+6, -y - height, width-12,
                                            height-12,
                                            color=color, batch=self.batch,
                                            ind=self.ind)
                    self.items.add(health_)
                    self.ind += 1

        #weapons
        for child in root.getchildren():
            if child.attrib['id'] == 'weapons':
                for rect in child:
                    atr = rect.attrib
                    x = float(atr['x'])
                    y = float(atr['y'])
                    width = float(atr['width'])
                    height = float(atr['height'])
                    weapstr = atr['weapon']
                    color = weaponcolors[weapstr]
                    respawn = timers['weapons']
                    if self.server:
                        w = allweapons[weapstr]
                        w_ = w(0, 0, x=x, y=-y-height, width=width,
                               height=height, respawn=respawn, color=color,
                               ind=self.ind, batch=self.batch)
                        self.items.add(w_)
                    else:
                        w_ = Triangle(x=x+6, y=-y-height, width=width-12,
                                      height=height-12, color=color,
                                      ind=self.ind,
                                      batch=self.batch, keystr=weapstr)
                        self.items.add(w_)
                    self.ind += 1

        #ammo
        for child in root.getchildren():
            if child.attrib['id'] == 'ammo':
                for rect in child:
                    atr = rect.attrib
                    x = float(atr['x'])
                    y = float(atr['y'])
                    width = float(atr['width'])
                    height = float(atr['height'])
                    weapstr = atr['weapon']
                    color = weaponcolors[weapstr]
                    max_ammo, ammoval = ammo_values[weapstr]
                    respawn = timers['weapons']
                    if self.server:
                        w_ = Ammo(x=x, y=-y-height, width=width,
                                  height=height, respawn=respawn, color=color,
                                  ind=self.ind, batch=self.batch,
                                  max_ammo=max_ammo, ammoval=ammoval,
                                  keystring=weapstr)
                        self.items.add(w_)
                    else:
                        w_ = AmmoTriangle(x=x+6, y=-y-height, width=width-12,
                                          height=height-12, color=color,
                                          ind=self.ind,
                                          batch=self.batch, keystr=weapstr)
                        self.items.add(w_)
                    self.ind += 1

        #tele
        for child in root.getchildren():
            if child.attrib['id'] == 'teles':
                for rect in child:
                    atr = rect.attrib
                    x = float(atr['x'])
                    y = float(atr['y'])
                    width = float(atr['width'])
                    height = float(atr['height'])
                    destination = vec2(float(atr['dest_x']),
                                       float(atr['dest_y']))
                    dest_sign = int(atr['dest_sign'])
                    color = (255, 255, 0)
                    max_ammo, ammoval = ammo_values[weapstr]
                    if self.server:
                        w_ = Teleporter(x=x, y=-y-height, width=width,
                                        height=height, color=color,
                                        ind=self.ind, destination=destination,
                                        dest_sign=dest_sign)
                        self.items.add(w_)
                    else:
                        w_ = DrawableTeleporter(x=x, y=-y-height, width=width,
                                                height=height, color=color,
                                                batch=self.batch)
                        self.items.add(w_)
                    self.ind += 1

    def draw(self):
        self.batch.draw()

    def serverupdate(self, itemid, spawn):
        self.items.fromserver(itemid, spawn)
