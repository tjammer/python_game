from collision.caabb import cAABB as AABB


timers = {'armor': 20,
          'health': 35,
          'weapons': 20}

armors = {50: ((255, 255, 0), 100),
          100: ((255, 0, 0), 200),
          25: ((0, 179, 0), 50)}

health = {25: ((179, 255, 0), 100),
          50: ((255, 128, 0), 100),
          100: ((0, 255, 255), 200)}


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


class Ammo(AABB):
    """docstring for Ammo"""
    def __init__(self, max_ammo, ammoval, keystring, respawn, ind,
                 *args, **kwargs):
        super(Ammo, self).__init__(*args, **kwargs)
        self.max_ammo = max_ammo
        self.ammoval = ammoval
        self.keystr = keystring
        self.respawn = respawn
        self.ind = ind
        self.inactive = False

    def apply(self, player):
        try:
            if player.weapons.weapons[self.keystr].ammo < self.max_ammo:
                player.weapons.weapons[self.keystr].ammo += self.ammoval
                if player.weapons.weapons[self.keystr].ammo > self.max_ammo:
                    player.weapons.weapons[self.keystr].ammo = self.max_ammo
                self.inactive = self.respawn
                return True
        except KeyError:
            pass
        return False


class ItemManager(object):
    """docstring for ItemManager"""
    def __init__(self, batch, renderhook):
        super(ItemManager, self).__init__()
        self.items = []
        self.batch = batch
        self.renderhook = renderhook

    def __iter__(self):
        return self.get_items()

    def __getitem__(self, key):
        return self.items[key]

    def add(self, item):
        self.items.append(item)

    def apply(self, player, item):
        id = self.items.index(item)
        return self.items[id].apply(player)

    def update(self, dt, func):
        for item in self.get_inactive():
            item.inactive -= dt
            if item.inactive <= 0:
                item.inactive = False
                func(item)

    def get_items(self):
        return (item for item in self.items if not item.inactive)

    def get_inactive(self):
        return (item for item in self.items if item.inactive)

    def send_mapstate(self, func, address):
        pl = IdDump(-1)
        for item in self.get_inactive():
            func(item, pl, address)

    def fromserver(self, itemid, spawn):
        id = itemid
        if spawn:
            self.items[id].inactive = False
            self.items[id].add(self.batch)
            self.renderhook(id, spawn=True)
        else:
            self.items[id].inactive = True
            #self.items[id].remove()
            self.renderhook(id, taken=True)


class IdDump(object):
    """docstring for IdDump"""
    def __init__(self, id):
        super(IdDump, self).__init__()
        self.id = id
