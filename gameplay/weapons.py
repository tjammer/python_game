from collision.rectangle import Rectangle


class Melee(object):
    """docstring for Melee"""
    def __init__(self, dmg, server, dispatch_proj, id):
        super(Melee, self).__init__()
        self.dmg = 40
        self.knockback = 700
        self.reload_t = 400
        self.dispatch_proj = dispatch_proj
        self.id = id
        self.ammo = 1

    def on_fire(pl_center, aim_pos):
        temp = aim_pos - pl_center
        direc = temp / temp.mag()
        proj = Projectile(self.dmg, self.knockback, self.id, *direc, 50, 50)
        self.dispatch_proj(proj)
        self.ammo += 1


class Weapon(object):
    """BaseWeapon class for other to inherit from"""
    def __init__(self, server, dmg=1, knockback=0, reload_t=0,
                 ammo=0, max_ammo=100, start_ammo=5):
        super(Weapon, self).__init__()
        #dmg per hit
        self.dmg = dmg
        self.knockback = knockback
        #time the weapon is active when firing
        self.reload_t = reload_t
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.start_ammo = start_ammo
        self.active = False
        #bool to register if weapon is projectile or hitscanweapn

    def on_fire(self, pl_center, aim_pos):
        pass

    def fire(self, pl_center, aim_pos):
        if not self.active and self.ammo > 0:
            self.on_fire(pl_center, aim_pos)
            self.ammo -= 1
        elif not self.ammo:
            raise NoAmmoError

    def reload(self):
        pass


class NoAmmoError(Exception):
    def __init__(self):
        pass


class Projectile(Rectangle):
    """docstring for Projectile"""
    #x and y are center positions for convenience
    def __init__(self, dmg, knockback, id, x, y, width, height):
        super(Projectile, self).__init__(x - width / 2, y - height / 2,
                                         width, height)
        self.dmg = dmg
        self.knockback = knockback
        #playerid for collision
        self.id = id

    def on_hit(self):
        pass
