from movement import Movement
from network_utils import protocol_pb2 as proto
from state import vec2, state
from menu.menu_events import Events
from gameplay.weapons import WeaponsManager
from options import colors, Options
try:
    from graphics.primitives import Rect
except:
    from collision.aabb import AABB as Rect

pext = vec2(32, 72)
phext = pext / 2


class Player(Events):
    """docstring for player"""
    def __init__(self, server=False, dispatch_proj=None, id=False, batch=None,
                 renderhook=None):
        super(Player, self).__init__()
        self.state = state(vec2(100, 130), vec2(0, 0), 100)
        self.move = Movement(*self.state.pos)
        self.dispatch_proj = dispatch_proj
     # spawning player at 0,0, width 32 = 1280 / 40. and height 72 = 720/10.
        self.Rect = Rect
        if id:
            self.id = id
            self.weapons = WeaponsManager(self.dispatch_proj, self.id)
        #self.color = Options()['color']  #(0, 204, 255)
        self.set_color(Options()['color'])
        self.rect = self.Rect(0, 0, pext.x, pext.y, self.color, isplayer=True,
                              batch=batch)
        #input will be assigned by windowmanager class
        self.input = proto.Input()
        self.listeners = {}
        self.ready = False
        self.renderhook = renderhook

    def update(self, dt, rectgen, state=False, input=False):
        if not state:
            state = self.state
        if not input:
            input = self.input
        self.rect.vel = self.move.get_vel(dt, state, input)
        self.rect.update(*state.pos)
        self.collide(dt, rectgen, state)
        self.weapons.update(dt, state, input)
        self.state.update(dt, state)
        if self.renderhook:
            self.renderhook(self, update=True)

    def specupdate(self, dt):
        if self.input.up:
            self.state.pos.y += 1000 * dt
        if self.input.right:
            self.state.pos.x += 1000 * dt
        if self.input.left:
            self.state.pos.x -= 1000 * dt
        if self.input.down:
            self.state.pos.y -= 1000 * dt

    def client_update(self, s_state, scale):
        easing = .3
        snapping_distance = 20 * scale.mag()

        diff = vec2(s_state.pos.x - self.state.pos[0],
                    s_state.pos.y - self.state.pos[1])
        len_diff = diff.mag()

        if len_diff > snapping_distance:
            self.state.pos = s_state.pos
        elif len_diff > .1:
            self.state.pos += diff * easing
        self.state.vel = s_state.vel
        self.rect.update(*self.state.pos)
        self.state.update(0, s_state)
        self.state.conds = s_state.conds
        if self.renderhook:
            self.renderhook(self, update=True)

    def predict(self, dt, rectgen):
        self.rect.vel = self.move.get_vel(dt, self.state, self.input)
        self.rect.update(*self.state.pos)
        self.collide(dt, rectgen, self.state)
        self.weapons.update(dt, self.state, self.input)
        if self.renderhook:
            self.renderhook(self, update=True)

    def draw(self):
        self.rect.draw()

    def collide(self, dt, rectgen, state):
        all_cols = [self.rect.sweep(obj, dt) for obj in rectgen]
        cols = [coldata for coldata in all_cols if coldata]
        try:
            xt = min(col[1] for col in cols if col[0].x != 0)
            xnorm, rct = [(col[0].x, rectgen[all_cols.index(col)])
                          for col in cols if col[1] == xt][0]
        except ValueError:
            xt = dt
            xnorm = 0.
        try:
            yt = min(col[1] for col in cols if col[0].y != 0)
            ynorm = [col[0].y for col in cols if col[1] == yt][0]
        except ValueError:
            yt = dt
            ynorm = 0.

        if xnorm:
            #check for stair
            stairoffset = 10
            testr = self.rect.copy()
            testr.update(testr.pos.x, testr.pos.y + stairoffset)
            first = testr.sweep(rct, dt)
            if not first:
                testr.update(testr.pos.x + testr.sign_of(testr.vel.x) * 30,
                             testr.pos.y)
                testr.vel.x = 0
                second = testr.sweep(rct, float('Inf'))
                if second:
                    s1 = testr.vel.y * second[1]
                    s = stairoffset + s1
                    t = s / testr.vel.y
                    if not abs(t) == float('Inf'):
                        yt = t
                        xnorm = 0
                        ynorm = -1

        dt = vec2(xt, yt)
        norm = vec2(xnorm, ynorm)
        self.resolve_sweep(norm, dt, state)

    def resolve_sweep(self, normal, dt, state):
        self.state.pos, self.state.vel = self.move.step(dt, state.pos)
        self.rect.update(*self.state.pos)
        self.state.vel.x *= normal.x == 0.
        self.state.vel.y *= normal.y == 0.
        self.move.resolve_coll(self.state.pos, self.state.vel)
        if normal.y < 0:
            self.state.set_cond('onGround')
        elif normal.x > 0:
            self.state.set_cond('onRightWall')
        elif normal.x < 0:
            self.state.set_cond('onLeftWall')
        elif normal.x == 0. and normal.y == 0.:
            self.determine_state()

    def resolve_collision(self, ovrlap, axis, angle):
        self.state.pos[0] = self.rect.x1 - ovrlap * axis[0]
        self.state.pos[1] = self.rect.y1 - ovrlap * axis[1]
        self.state.vel[0] *= axis[1] > 0
        self.state.vel[1] *= axis[0] > 0
        self.rect.update(*self.state.pos)
        self.move.resolve_coll(self.state.pos, self.state.vel)
        if axis[1] > 0 and ovrlap < 0:
            #self.move.conds['on_ground'] = True
            self.state.set_cond('onGround')
            #self.move.angle = angle
        elif axis[0] > 0:
            if ovrlap > 0:
                self.state.set_cond('onRightWall')
            elif ovrlap < 0:
                self.state.set_cond('onLeftWall')

    def determine_state(self):
        if self.state.vel.y < 0:
            self.state.set_cond('descending')

    def spawn(self, x, y, other=False):
        self.state.pos = vec2(x, y)
        self.state.vel = vec2(0, 0)
        self.state.hp = 100
        self.state.armor = 0
        self.state.isDead = False
        self.state.frozen = False
        if isinstance(self.rect, Rect):
            self.rect.update_color(self.color)
        self.weapons.reset()

    def get_id(self, id, name):
        self.id = id
        self.name = name
        self.weapons = WeaponsManager(self.dispatch_proj, self.id)
        self.renderhook(self, add=True)

    def die(self):
        self.state.isDead = 5
        if isinstance(self.rect, Rect):
            self.rect.update_color([128] * 3)

    def freeze(self):
        self.state.frozen = True

    def set_color(self, cstr):
        self.color = colors[cstr]

    def remove_from_view(self):
        self.renderhook(self, remove=True)

    def add_to_view(self):
        self.renderhook(self, add=True)


class DrawablePlayer(object):
    """docstring for DrawablePlayer"""
    def __init__(self, player, batch, fac):
        super(DrawablePlayer, self).__init__()
        self.state = player.state
        self.rect = player.rect.copy()
        self.batch = batch
        self.scale(fac)

    def scale(self, fac):
        self.rect.pos *= fac
        self.rect.width *= fac.x
        self.rect.height *= fac.y
        self.rect.add(self.batch)

    def update(self, player, fac):
        self.rect.update(*(vec2(*player.rect.pos) * fac))
        if player.rect.color != self.rect.color:
            self.rect.update_color(player.rect.color)

    def remove(self):
        self.rect.remove()
