class Weapon(object):
    """BaseWeapon class for other to inherit from"""
    def __init__(self, dmg, knockback, reload_t, ammo, max_ammo, start_ammo,
                 projectile):
        super(Weapon, self).__init__()
        #dmg per hit
        self.dmg = dmg
        self.knockback = knockback
        #time the weapon is active when firing
        self.reload_t = reload_t
        self.ammo = ammo
        self.max_ammo = max_ammo
        self.start_ammo = start_ammo
        #bool to register if weapon is projectile or hitscanweapn
        self.projectile = projectile

    def fire(self):
        pass

    def reload(self):
        pass


class Projectile(object):
    """docstring for Projectile"""
    def __init__(self, dmg, knockback):
        super(Projectile, self).__init__()
        self.dmg = dmg
        self.knockback = knockback
