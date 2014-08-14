from collision.aabb import AABB as Rectangle
from player.state import vec2
from network_utils import protocol_pb2 as proto
from graphics.primitives import Rect


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
                               lifetime=self.proj_lifetime,
                               offset=offset, ppos=pos)
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
        proj = BlasterProjectile(x=pos.x+16, y=pos.y+32,
                                 width=15, height=15, vel=self.vel,
                                 direc=direc, lifetime=self.proj_lifetime,
                                 dmg=40, id=self.id)
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
                 lifetime=0.1, offset=None, ppos=None):
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
        self.type = None
        self.offset = offset
        self.ppos = ppos
        self.canthurt = 0.5

    def on_hit(self, player=None):
        pass

    def updateproj(self, dt, mapgen, playergen):
        self.lifetime -= dt
        if self.canthurt:
            self.canthurt -= dt
            if self.canthurt <= 0:
                self.canthurt = False
        return self.collide(dt, mapgen, playergen)

    def collide(self, dt, mapgen, playergen):
        all_collisions = ((self.sweep(obj.rect, dt), obj.id)
                          for obj in playergen)
        collisions = [coldata for coldata in all_collisions if coldata[0]]
        id = False
        try:
            xt = min(col[0][1] for col in collisions if col[0][0].x != 0)
            id = [col[1] for col in collisions if col[0][1] == xt][0]
        except (TypeError, ValueError):
            xt = dt
        try:
            yt = min(col[0][1] for col in collisions if col[0][0].y != 0)
            if yt < xt:
                id = [col[1] for col in collisions if col[0][1] == yt][0]
        except (TypeError, ValueError):
            yt = dt
        dt_ = vec2(xt, yt)
        if not id:
            all_collisions = (self.sweep(obj, dt) for obj in mapgen)
            collisions = [coldata for coldata in all_collisions if coldata]
            try:
                xt = min(col[1] for col in collisions if col[0].x != 0)
            except (TypeError, ValueError):
                xt = dt
            try:
                yt = min(col[1] for col in collisions if col[0].y != 0)
            except (TypeError, ValueError):
                yt = dt
            dt_ = vec2(xt, yt)
            if (dt_.x < dt or dt_.y < dt):
                id = -1
        return self.resolve_sweep(dt_, id)

    def resolve_sweep(self, dt, id):
        pos = self.pos + self.vel * dt
        self.update(*pos)
        if not id:
            return False
        elif id == self.id and self.canthurt:
            return False
        else:
            return id

    def pass_pos(self, pos, vel):
        self.vel, self.pos = vel, pos


class MeleeProjectile(Projectile):
    """docstring for MeleeProjectile"""
    def __init__(self, *args, **kwargs):
        super(MeleeProjectile, self).__init__(*args, **kwargs)
        self.type = proto.melee
        self.rectoffset = vec2(16 - self.width / 2, 36 - self.height / 2)
        self.vel = vec2(0, 0)
        self.ids = [self.id]

    def on_hit(self, players=None):
        for player in players:
            if player.id not in self.ids:
                self.damage_player(player, self)
                player.state.vel += self.direc * self.knockback
                self.ids.append(player.id)
        return False

    def collide(self, dt, mapgen, playergen):
        return [player for player in playergen if self.overlaps(player.rect)]

    def updateproj(self, dt, mapgen, playergen):
        self.update(*(vec2(*self.ppos) + self.offset + self.rectoffset))
        self.lifetime -= dt
        return self.collide(dt, mapgen, playergen)

    def resolve_sweep(self, dt, id):
        if not id:
            return False
        else:
            return id


class BlasterProjectile(Projectile):
    """docstring for BlasterProjectile"""
    def __init__(self, *args, **kwargs):
        super(BlasterProjectile, self).__init__(*args, **kwargs)
        self.type = proto.blaster

    def on_hit(self, player=None):
        posx = self.pos.x
        posy = self.pos.y
        hwidth = 102
        proj = BlasterExplosion(dmg=10, knockback=400, id=self.id,
                                x=posx, y=posy,
                                width=hwidth*2,
                                height=hwidth*2, vel=0, direc=vec2(0, 0),
                                lifetime=0.05)
        self.dispatch_proj(proj)
        #direct dmg
        if player:
            self.damage_player(player, self)
        return True


class Explosion(Projectile):
    """docstring for Explosion"""
    def __init__(self, *args, **kwargs):
        super(Explosion, self).__init__(*args, **kwargs)
        self.players = []

    def collide(self, dt, mapgen, playergen):
        return [player for player in playergen if self.overlaps(player.rect)]

    def on_hit(self, players):
        for player in players:
            if player not in self.players:
                self.damage_player(player, self)
                direc = self.center - player.rect.center
                player.state.vel -= direc / direc.mag() * self.knockback
            self.players.append(player)
        return False


class BlasterExplosion(Explosion):
    """docstring for BlasterExplosion"""
    def __init__(self, *args, **kwargs):
        super(BlasterExplosion, self).__init__(*args, **kwargs)
        self.type = proto.explBlaster


class ProjectileManager(object):
    """docstring for ProjectileManager"""
    def __init__(self, players, _map, dmg_func):
        super(ProjectileManager, self).__init__()
        self.projs = []
        self.todelete = []
        self.send_ = None
        self.proj_num = 0
        self.message = proto.Message()
        self.message.type = proto.projectile
        #for collisions
        self.players = players
        self.map = _map
        self.damage_player = dmg_func

    def __iter__(self):
        return iter(self.projs)

    def __getitem__(self, key):
        return self.projs[key]

    def __len__(self):
        return len(self.projs)

    def update(self, dt):
        for proj in self.projs:
            mapgen = (rect for rect in self.map.quad_tree.retrieve([], proj))
            playergen = (player for player in self.players.itervalues())
            coll = proj.updateproj(dt, mapgen, playergen)
            if coll:
                try:
                    player = self.players[coll]
                except KeyError:
                    player = False
                except TypeError:
                    #in case of explosions coll: list of players in expl radius
                    player = coll
                self.resolve_collision(proj, player)
            if proj.lifetime < 0:
                self.todelete.append(proj)
        #loop over copy of list to make deletion possible
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

    def resolve_collision(self, proj, player):
        #self.todelete.append(proj)
        if proj.on_hit(player):
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
        proj.damage_player = self.damage_player
        self.projs.append(proj)

    def send(self, proj, toDelete=False):
        projectile = proto.Projectile()
        projectile.projId = proj.projId
        projectile.type = proj.type
        projectile.posx, projectile.posy = proj.pos.x, proj.pos.y
        projectile.velx, projectile.vely = proj.vel.x, proj.vel.y
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
        if not self.data.toDelete:
            vel = vec2(self.data.velx, self.data.vely)
            pos = vec2(self.data.posx, self.data.posy)
            if ind in self.projs:
                self.projs[ind].update(*pos)
            else:
                if self.data.type == proto.melee:
                    self.projs[ind] = Rect(pos.x, pos.y, width=70, height=70,
                                           color=(255, 0, 0))
                    self.projs[ind].vel = vel
                elif self.data.type == proto.blaster:
                    self.projs[ind] = Rect(pos.x, pos.y, width=15, height=15,
                                           color=(255, 0, 0))
                    self.projs[ind].vel = vel
                elif self.data.type == proto.explBlaster:
                    self.projs[ind] = Rect(pos.x, pos.y, width=204, height=204,
                                           color=(255, 0, 150))
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
            pos = proj.pos + proj.vel * dt
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
        self._allweapos = {'w0': Melee, 'w1': Blaster}
        self._stringweaps = {'w0': 'melee', 'w1': 'blaster'}
        #start only with melee
        self.weapons = {'w0': Melee(dispatch_proj, id),
                        'w1': Blaster(dispatch_proj, id)}
        self.current_w = self.weapons['w0']
        self.current_s = self._stringweaps['w0']
        self.wli = 0
        self.hudhook = False

    def fire(self, pos, aim_pos):
        try:
            self.current_w.fire(pos, aim_pos)
            if self.hudhook:
                self.hudhook(ammo=str(self.current_w.ammo))
        except NoAmmoError:
            if self.hudhook:
                self.hudhook(text='no ammo')

    def update(self, dt, state, input):
        if state.isDead or state.frozen:
            return 0
        if input.att:
            self.fire(state.pos, vec2(input.mx, input.my))
        if input.w0:
            self.switch_to('w0')
        elif input.w1:
            self.switch_to('w1')
        self.current_w.update(dt)

    def switch_to(self, key):
        if self.current_w != self.weapons[key]:
            active = self.current_w.active
            self.current_w = self.weapons[key]
            self.current_w.active = active
            self.current_s = self._stringweaps[key]
            if self.hudhook:
                self.hudhook(weapon=self.current_s)

    def hook_hud(self, hudhook):
        self.hudhook = hudhook

    def reset(self):
        self.current_w = self.weapons['w0']
        self.current_s = self._stringweaps['w0']
        if self.hudhook:
                self.hudhook(weapon=self.current_s)
