from collision.rectangle import Rectangle
from player.state import vec2


class Weapon(object):
    """BaseWeapon class for other to inherit from"""
    def __init__(self, dmg=1, knockback=0, reload_t=0,
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

    def on_fire(self, pl_center, aim_pos):
        pass

    def fire(self, pl_center, aim_pos):
        if not self.active and self.ammo > 0:
            self.active = self.reload_t
            try:
                self.on_fire(pl_center, aim_pos)
            except TypeError:
                pass
            self.ammo -= 1
        elif not self.ammo:
            raise NoAmmoError

    def reload(self):
        pass

    def update(self, dt):
        dt = dt * 10**3
        if self.active:
            self.active = self.active - dt
            if self.active < 0:
                self.active = 0


class Melee(Weapon):
    """docstring for Melee"""
    def __init__(self, dispatch_proj, id):
        super(Melee, self).__init__()
        self.dmg = 40
        self.knockback = 700
        self.reload_t = 400
        self.dispatch_proj = dispatch_proj
        self.id = id
        self.ammo = 1
        self.vel = 0
        self.selfhit = False
        self.proj_lifetime = 1. / 12

    def on_fire(self, pl_center, aim_pos):
        self.ammo += 1
        temp = aim_pos - pl_center
        direc = temp / temp.mag()
        pos = pl_center + direc * 50
        proj = MeleeProjectile(self.dmg, self.knockback, self.id, pos.x, pos.y,
                               width=50, height=50, vel=self.vel,
                               selfhit=self.selfhit, direc=direc,
                               lifetime=self.proj_lifetime)
        self.dispatch_proj(proj)


class NoAmmoError(Exception):
    def __init__(self):
        pass


class Projectile(Rectangle):
    """docstring for Projectile"""
    #x and y are center positions for convenience
    def __init__(self, dmg, knockback, id, x, y, width, height, vel, selfhit,
                 direc, lifetime):
        super(Projectile, self).__init__(x - width / 2, y - height / 2,
                                         width, height)
        self.dmg = dmg
        self.knockback = knockback
        #playerid for collision
        self.id = id
        #vel is float
        self.direc = direc
        self.vel = direc * vel
        self.selfhit = selfhit
        self.lifetime = lifetime

    def on_hit(self, ovr, axis, player=None):
        pass

    def updateproj(self, dt):
        pos = vec2(self.x1, self.y1) + self.vel * dt
        self.update(*pos)
        self.lifetime -= dt


class MeleeProjectile(Projectile):
    """docstring for MeleeProjectile"""
    def __init__(self, dmg, knockback, id, x, y, width, height, vel, selfhit,
                 direc, lifetime):
        super(MeleeProjectile, self).__init__(dmg, knockback, id, x, y, width,
                                              height, vel, selfhit, direc,
                                              lifetime)

    def on_hit(self, ovr, axis, player=None):
        if player and player.id != self.id:
            player.state.hp -= self.dmg
            player.state.vel += self.direc * self.knockback


class ProjectileManager(object):
    """docstring for ProjectileManager"""
    def __init__(self, players, Map):
        super(ProjectileManager, self).__init__()
        self.projs = []
        self.todelete = []
        #dict of players for collision
        self.players = players
        #map for collision
        self.map = Map

    def __iter__(self):
        return iter(self.projs)

    def __getitem__(self, key):
        return self.projs[key]

    def __len__(self):
        return len(self.projs)

    def update(self, dt):
        for proj in self.projs:
            proj.updateproj(dt)
            if proj.lifetime < 0:
                self.todelete.append(proj)
        #loop over copy of list to make deletion possible
        for proj in reversed(self.projs):
            self.collide(proj)
        self.del_projectiles()

    def collide(self, proj):
        #extra function to be able to return when coll is found
        collided = False
        for player in self.players.itervalues():
            coll = proj.collides(player.rect)
            if coll:
                ovr, axis = coll
                self.resolve_collision(ovr, axis, proj, player)
                collided = True
        if not collided:
            for rect in self.map.quad_tree.retrieve([], proj):
                coll = proj.collides(rect)
                if coll:
                    ovr, axis = coll
                    self.resolve_collision(ovr, axis, proj)

    def resolve_collision(self, ovr, axis, proj, player=None):
        self.todelete.append(proj)
        proj.on_hit(ovr, axis, player)

    def del_projectiles(self):
        for proj in reversed(self.todelete):
            self.projs.remove(proj)
            while proj in self.todelete:
                self.todelete.remove(proj)

    def add_projectile(self, proj):
        self.projs.append(proj)


class WeaponsManager(object):
    """docstring for WeaponsManager"""
    def __init__(self, dispatch_proj, id):
        super(WeaponsManager, self).__init__()
        self.dispatch_proj = dispatch_proj
        self.id = id
        self._allweapos = {'melee': Melee}
        #start only with melee
        self.weapons = [Melee(dispatch_proj, id)]
        self.current_w = self.weapons[0]

    def fire(self, pl_center, aim_pos):
        try:
            self.current_w.fire(pl_center, aim_pos)
        except NoAmmoError:
            print 'no ammmo'

    def update(self, dt):
        self.current_w.update(dt)
