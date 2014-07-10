from collision.rectangle import Rectangle
from player.state import vec2
from network_utils import protocol_pb2 as proto
from graphics.primitives import Rect
from math import atan, acos

pi = acos(0)


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

    def on_fire(self, pos, aim_pos):
        pass

    def fire(self, pos, aim_pos):
        if not self.active and self.ammo > 0:
            self.active = self.reload_t
            try:
                self.on_fire(pos, aim_pos)
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
        self.knockback = 300
        self.reload_t = 400
        self.dispatch_proj = dispatch_proj
        self.id = id
        self.ammo = 1
        self.vel = 0
        self.selfhit = False
        self.proj_lifetime = 1. / 12
        self.reach = 40

    def on_fire(self, pos, aim_pos):
        self.ammo += 1
        rectoffset = vec2(16, 36)
        temp = aim_pos - pos - rectoffset
        direc = temp / temp.mag()
        if temp.mag() <= self.reach:
            offset = direc * temp.mag()
        else:
            offset = direc * self.reach
        npos = pos + rectoffset + offset
        proj = MeleeProjectile(self.dmg, self.knockback, self.id, npos.x,
                               npos.y, width=70, height=70, vel=self.vel,
                               selfhit=self.selfhit, direc=direc,
                               lifetime=self.proj_lifetime, pos=pos,
                               offset=offset)
        self.dispatch_proj(proj)


class Blaster(Weapon):
    """docstring for Blaster"""
    def __init__(self, dispatch_proj, id):
        super(Blaster, self).__init__()
        self.dispatch_proj = dispatch_proj
        self.id = id
        self.reload_t = 1000
        self.ammo = 1
        self.vel = 1000
        self.selfhit = True
        self.proj_lifetime = 10

    def on_fire(self, pos, aim_pos):
        self.ammo += 1
        rectoffset = vec2(16, 32)
        temp = aim_pos - pos - rectoffset
        direc = temp / temp.mag()
        proj = BlasterProjectile(x=pos.x+16+direc.x*32, y=pos.y+32+direc.y*72,
                                 width=15, height=15, vel=self.vel,
                                 direc=direc, lifetime=self.proj_lifetime)
        proj.dispatch_proj = self.dispatch_proj
        self.dispatch_proj(proj)


class NoAmmoError(Exception):
    def __init__(self):
        pass


class Projectile(Rectangle):
    """docstring for Projectile"""
    #x and y are center positions for convenience
    def __init__(self, dmg=10, knockback=10, id=0, x=0, y=0, width=100,
                 height=100, vel=10, selfhit=False, direc=vec2(10, 0),
                 lifetime=0.1, pos=None, offset=None, angle=0):
        super(Projectile, self).__init__(x - width / 2, y - height / 2,
                                         width, height, angle=angle)
        self.dmg = dmg
        self.knockback = knockback
        #playerid for collision
        self.id = id
        #vel is float
        self.direc = direc
        self.vel = direc * vel
        self.selfhit = selfhit
        self.lifetime = lifetime
        self.type = None
        self.pos = pos
        self.offset = offset

    def on_hit(self, ovr, axis, player=None):
        pass

    def updateproj(self, dt):
        pos = vec2(self.x1, self.y1) + self.vel * dt
        self.update(*pos)
        self.lifetime -= dt

    def pass_pos(self, pos, vel):
        self.vel, self.pos = vel, pos


class MeleeProjectile(Projectile):
    """docstring for MeleeProjectile"""
    def __init__(self, *args, **kwargs):
        super(MeleeProjectile, self).__init__(*args, **kwargs)
        self.type = proto.melee
        self.rectoffset = vec2(16 - self.width / 2, 36 - self.height / 2)

    def on_hit(self, ovr, axis, player=None):
        if player and player.id != self.id:
            player.state.hp -= self.dmg
            player.state.vel += self.direc * self.knockback
        #return if delete proj, in case of melee never
        return False

    def updateproj(self, dt):
        self.update(*(vec2(*self.pos) + self.offset + self.rectoffset))
        self.lifetime -= dt


class BlasterProjectile(Projectile):
    """docstring for BlasterProjectile"""
    def __init__(self, *args, **kwargs):
        super(BlasterProjectile, self).__init__(*args, **kwargs)
        self.type = proto.blaster

    def on_hit(self, ovr, axis, player=None):
        posx = self.x1 - ovr * axis[0]
        posy = self.y1 - ovr * axis[1]
        hwidth = 51
        proj = BlasterExplosion(dmg=50, knockback=400, id=self.id,
                                x=posx+hwidth*2./3, y=posy+hwidth*2./3,
                                width=hwidth*2,
                                height=hwidth*2, vel=0, direc=vec2(0, 0),
                                lifetime=0.05)
        self.dispatch_proj(proj)
        return True


class BlasterExplosion(Projectile):
    """docstring for BlasterExplosion"""
    def __init__(self, *args, **kwargs):
        super(BlasterExplosion, self).__init__(*args, **kwargs)
        self.type = proto.explBlaster

    def on_hit(self, ovr, axis, player=None):
        if player:
            player.state.hp -= self.dmg
            player.state.vel -= (self.center
                                 - player.rect.center) * 5
        return False


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
        self.send_ = None
        self.proj_num = 0
        self.message = proto.Message()
        self.message.type = proto.projectile

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
        for proj in self.projs:
            self.collide(proj)
        self.del_projectiles()
        self.send_all()

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
        #self.todelete.append(proj)
        if proj.on_hit(ovr, axis, player):
            self.todelete.append(proj)

    def del_projectiles(self):
        for proj in set(self.todelete):
            self.projs.remove(proj)
            self.send(proj, toDelete=True)
            while proj in self.todelete:
                self.todelete.remove(proj)

    def add_projectile(self, proj):
        self.proj_num += 1
        proj.projId = self.proj_num
        self.projs.append(proj)

    def send(self, proj, toDelete=False):
        projectile = proto.Projectile()
        projectile.projId = proj.projId
        projectile.type = proj.type
        projectile.posx, projectile.posy = proj.x1, proj.y1
        projectile.velx, projectile.vely = proj.vel.x, proj.vel.y
        projectile.angle = proj.angle
        projectile.toDelete = toDelete
        self.message.projectile.CopyFrom(projectile)
        for player in self.players.itervalues():
            self.send_(self.message.SerializeToString(), player.address)

    def send_all(self):
        for proj in self.projs:
            self.send(proj)

    def receive_send(self, func):
        self.send_ = func


class ProjectileViewer(object):
    """docstring for ProjectileViewer"""
    def __init__(self):
        super(ProjectileViewer, self).__init__()
        self.projs = {}
        self.data = proto.Projectile()

    def process_proj(self, datagram):
        self.data.CopyFrom(datagram)
        ind = self.data.projId
        angle = self.data.angle * 180 / pi
        if not self.data.toDelete:
            vel = vec2(self.data.velx, self.data.vely)
            pos = vec2(self.data.posx, self.data.posy)
            if ind in self.projs:
                self.projs[ind].update(*pos)
            else:
                if self.data.type == proto.melee:
                    self.projs[ind] = Rect(pos.x, pos.y, width=70, height=70,
                                           color=(1., 0., 0.))
                    self.projs[ind].vel = vel
                elif self.data.type == proto.blaster:
                    self.projs[ind] = Rect(pos.x, pos.y, width=15, height=15,
                                           color=(1., 0., 0.), angle=angle)
                    self.projs[ind].vel = vel
                elif self.data.type == proto.explBlaster:
                    self.projs[ind] = Rect(pos.x, pos.y, width=102, height=102,
                                           color=(4., .2, .6))
                    self.projs[ind].vel = vel
                else:
                    raise ValueError
        else:
            try:
                del self.projs[ind]
            except KeyError:
                pass

    def update(self, dt):
        for proj in self.projs.itervalues():
            pos = vec2(proj.x1, proj.y1)
            pos += proj.vel * dt
            proj.update(*pos)

    def draw(self):
        for proj in self.projs.itervalues():
            proj.draw()


class WeaponsManager(object):
    """docstring for WeaponsManager"""
    def __init__(self, dispatch_proj, id):
        super(WeaponsManager, self).__init__()
        self.dispatch_proj = dispatch_proj
        self.id = id
        self._allweapos = {'melee': Melee}
        #start only with melee
        self.weapons = [Melee(dispatch_proj, id), Blaster(dispatch_proj, id)]
        self.current_w = self.weapons[0]
        self.wli = 0

    def fire(self, pos, aim_pos):
        try:
            self.current_w.fire(pos, aim_pos)
        except NoAmmoError:
            print 'no ammmo'

    def update(self, dt, state, input):
        if input.att:
            self.fire(state.pos, vec2(input.mx, input.my))
        if input.switch:
            self.switch()
        self.current_w.update(dt)

    def switch(self):
        if not self.current_w.active:
            self.wli += 1
            if self.wli == len(self.weapons):
                self.wli = 0
            self.current_w = self.weapons[self.wli]
            self.current_w.active = self.current_w.reload_t
            print 'weapon switched'
