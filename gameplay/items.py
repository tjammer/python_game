from collision.aabb import AABB
from graphics.primitives import Rect


class Armor(AABB):
    """docstring for Armor"""
    def __init__(self, value, bonus, respawn, ind, *args, **kwargs):
        super(Armor, self).__init__(*args, **kwargs)
        self.inactive = False
        self.value = value
        self.bonus = bonus
        self.respawn = respawn
        self.ind = ind

    def apply(self, player, maxarmor=200):
        if player.state.armor == maxarmor and not self.bonus:
            return False
        else:
            player.state.armor += self.value
            if not self.bonus and player.state.armor > maxarmor:
                player.state.armor = maxarmor
            self.inactive = self.respawn
            return True


class DrawableArmor(Rect):
    """docstring for DrawableArmor"""
    def __init__(self, value, bonus, respawn, ind, *args, **kwargs):
        super(DrawableArmor, self).__init__(*args, **kwargs)
        self.inactive = False
        self.value = value
        self.bonus = bonus
        self.respawn = respawn
        self.ind = ind


class ItemManager(object):
    """docstring for ItemManager"""
    def __init__(self):
        super(ItemManager, self).__init__()
        self.items = []

    def __iter__(self):
        return self.get_items()

    def add(self, item):
        self.items.append(item)

    def apply(self, player, item):
        id = self.items.index(item)
        return self.items[id].apply(player)

    def update(self, dt, func):
        inactivegen = (it for it in self.items if it.inactive)
        for item in inactivegen:
            item.inactive -= dt
            if item.inactive <= 0:
                item.inactive = False
                func(item)

    def get_items(self):
        return (item for item in self.items if not item.inactive)

    def fromserver(self, itemid, spawn):
        id = itemid
        if spawn:
            self.items[id].inactive = False
        else:
            self.items[id].inactive = True
