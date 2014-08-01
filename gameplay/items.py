from collision.aabb import AABB
from graphics.primitives import Rect


armors = {50: ((1., 1., 0.), 100),
          100: ((1., 0., 0.), 200),
          10: ((0., .7, 0.), 50)}

health = {25: ((.7, 1., 0.), 100),
          50: ((1., .5, 0.), 100),
          100: ((0., 1., 1.), 200)}


class Armor(AABB):
    """docstring for Armor"""
    def __init__(self, value, bonus, respawn, ind, maxarmor, *args, **kwargs):
        super(Armor, self).__init__(*args, **kwargs)
        self.inactive = False
        self.value = value
        self.bonus = bonus
        self.respawn = respawn
        self.ind = ind
        self.maxarmor = maxarmor

    def apply(self, player):
        if player.state.armor >= self.maxarmor and not self.bonus:
            return False
        else:
            player.state.armor += self.value
            if not self.bonus and player.state.armor > self.maxarmor:
                player.state.armor = self.maxarmor
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


class Health(AABB):
    """docstring for Health"""
    def __init__(self, value, bonus, respawn, ind, maxhp, *args, **kwargs):
        super(Health, self).__init__(*args, **kwargs)
        self.inactive = False
        self.value = value
        self.bonus = bonus
        self.respawn = respawn
        self.ind = ind
        self.maxhp = maxhp

    def apply(self, player):
        if player.state.hp >= self.maxhp and not self.bonus:
            return False
        else:
            player.state.hp += self.value
            if not self.bonus and player.state.hp > self.maxhp:
                player.state.hp = self.maxhp
            self.inactive = self.respawn
            return True


class DrawableHealth(Rect):
    """docstring for DrawableHealth"""
    def __init__(self, *args, **kwargs):
        super(DrawableHealth, self).__init__(*args, **kwargs)
        self.inactive = False


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
