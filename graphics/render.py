import pyglet
from pyglet.gl import *
from player.cvec2 import cvec2 as vec2
from maps.map import DrawableMap
from player.player import DrawablePlayer
from network_utils import protocol_pb2 as proto
from graphics.primitives import Rect, DrawaAbleLine, TexQuad
from gameplay.weapons import spread, ProjContainer, weaponcolors
from collision.caabb import Line
from shader import OffscreenBuffer as FBO, Shader, vector
from model import Model
from os import path
from matrix import Matrix


class Render(object):
    def __init__(self, camera, window):
        super(Render, self).__init__()
        self.scene_batch = pyglet.graphics.Batch()
        self.static_batch = pyglet.graphics.Batch()
        self.camera = camera
        self.window = window
        # scaling factors
        self.scale = vec2(window.width / 1360., window.height / 765.)
        self.players = {}
        self.fbo = FBO(window.width, window.height)
        self.model = Model(path.join('graphics', 'metatest.dae'), self.scale.x)
        self.lighting = Shader('lighting')
        self.lighting.set('mvp', Matrix.orthographic(
            0., window.width, 0., window.height, 0, 1))
        self.lighting.set('lightPos', vector((-15, 15, 10)))
        self.screen = TexQuad(
            0, 0, window.width, window.height, self.fbo.textures[0].tex_coords)

    def draw(self):
        with self.fbo:
            self.fbo.clear()
            with self.camera as mvp:
                self.scene_batch.draw()
                self.model.draw(mvp)

        #send texture data to shader
        for i in range(3):
            glActiveTexture(GL_TEXTURE0 + i)
            glBindTexture(GL_TEXTURE_2D, self.fbo.textures[i].id)
        arr = c_int * 3
        self.lighting.set('texs', arr(self.fbo.textures[0].id,
                                      self.fbo.textures[1].id,
                                      self.fbo.textures[2].id))
        glActiveTexture(GL_TEXTURE0)

        #draw; for now scene batch like this, eventually it will also be 3d
        self.window.clear()
        with self.lighting:
            self.screen.draw()
        self.static_batch.draw()

    def maphook(self, map, add=False, spawn=False, remove=False, taken=False):
        if spawn:
            self.map.spawn(map)
        elif taken:
            self.map.taken(map)
        elif add:
            self.map = DrawableMap(map, self.scene_batch, self.scale)

    def playerhook(self, player, remove=False, update=False, add=False):
        id = player.id
        if update:
            self.players[id].update(player, self.scale)
        elif add:
            self.players[id] = DrawablePlayer(player, self.scene_batch,
                                              self.scale)
        elif remove:
            self.players[id].remove()
            del self.players[id]

    def update(self, dt):
        self.model.update(dt, self.players[1].state)


class ProjectileViewer(object):

    """docstring for ProjectileViewer"""

    def __init__(self, get_cent, batch, scale):
        super(ProjectileViewer, self).__init__()
        self.projs = {}
        self.data = proto.Projectile()
        self.batch = batch
        self.get_center = get_cent
        self.scale = scale
        self.scalemag = self.scale.mag()

    def process_proj(self, datagram):
        self.data.CopyFrom(datagram)
        ind = self.data.projId
        if not self.data.toDelete:
            vel = vec2(self.data.velx, self.data.vely)
            pos = vec2(self.data.posx, self.data.posy)
            if ind in self.projs:
                # self.projs[ind].update(*pos)
                self.correct(pos * self.scale, vel * self.scale, ind)
            else:
                if self.data.type == proto.melee:
                    self.projs[ind] = Rect(pos.x * self.scale.x,
                                           pos.y * self.scale.y, width=70,
                                           height=70,
                                           color=(255, 0, 0), batch=self.batch)
                    self.projs[ind].vel = vel
                    self.projs[ind].time = 0.09
                elif self.data.type == proto.blaster:
                    self.projs[ind] = Rect(pos.x * self.scale.x,
                                           pos.y * self.scale.y, width=10,
                                           height=10,
                                           color=weaponcolors['w3'],
                                           batch=self.batch)
                    self.projs[ind].vel = vel
                    self.projs[ind].time = 10.1
                elif self.data.type == proto.gl:
                    self.projs[ind] = Rect(pos.x * self.scale.x,
                                           pos.y * self.scale.y, width=15,
                                           height=10,
                                           color=weaponcolors['w4'],
                                           batch=self.batch)
                    self.projs[ind].vel = vel
                    self.projs[ind].time = 2.6
                elif self.data.type == proto.explBlaster:
                    self.projs[ind] = Rect(pos.x * self.scale.x,
                                           pos.y * self.scale.y, width=250,
                                           height=250,
                                           color=(255, 0, 150),
                                           batch=self.batch)
                    self.projs[ind].vel = vel
                    self.projs[ind].time = 0.06
                elif self.data.type == proto.explNade:
                    self.projs[ind] = Rect(pos.x * self.scale.x,
                                           pos.y * self.scale.y, width=250,
                                           height=250,
                                           color=(255, 0, 150),
                                           batch=self.batch)
                    self.projs[ind].vel = vel
                    self.projs[ind].time = 0.06
                elif self.data.type == proto.lg:
                    id = self.data.playerId
                    length = self.data.posx
                    playerhit = self.data.posy
                    center, mpos = self.get_center(id)
                    center = vec2(*center) * self.scale
                    mpos = vec2(*mpos) * self.scale
                    dr = mpos - center
                    drunit = dr / dr.mag()
                    length = (self.scale * drunit).mag() * length
                    line = DrawaAbleLine(center.x,
                                         center.y, dr.x, dr.y,
                                         length=length, batch=self.batch,
                                         color=weaponcolors['w2'])
                    if playerhit:
                        line.update_color((255, 0, 0))
                    line.time = 0.05
                    line.id = id
                    self.projs[ind] = line
                elif self.data.type == proto.sg:
                    id = self.data.playerId
                    playerhit = self.data.posy
                    center, mpos = self.get_center(id)
                    center = vec2(*center) * self.scale
                    mpos = vec2(*mpos) * self.scale
                    dr = mpos - center
                    dys = spread(dr.x, dr.y, angle=0.1, num=6)
                    cont = ProjContainer(0.05, id)
                    for dy in dys:
                        un = vec2(dr.x, dy)
                        un = un / un.mag()
                        line = DrawaAbleLine(center.x + un.x * 40,
                                             center.y + un.y * 40,
                                             dr.x, dy, length=100,
                                             batch=self.batch,
                                             color=weaponcolors['w1'])
                        if playerhit:
                            line.update_color((255, 0, 0))
                        cont.append(line)
                    self.projs[ind] = cont
                else:
                    raise ValueError
        else:
            try:
                self.projs[ind].remove()
                del self.projs[ind]
            except KeyError:
                pass

    def update(self, dt):
        todelete = []
        for key, proj in self.projs.iteritems():
            if isinstance(proj, Rect):
                if proj.color == weaponcolors['w4']:
                    proj.vel.y -= 1500 * dt
                pos = proj.pos + proj.vel * dt
                ##self.interpolate(key, pos)
                proj.update(*pos)
                proj.time -= dt
                if proj.time <= 0:
                    proj.remove()
                    todelete.append(key)
            elif isinstance(proj, Line):
                proj.time -= dt
                if proj.time <= 0:
                    proj.remove()
                    todelete.append(key)
                center, mpos = self.get_center(proj.id)
                center = vec2(*center) * self.scale
                mpos = vec2(*mpos) * self.scale
                proj.update(center.x, center.y, mpos[0], mpos[1])
            elif isinstance(proj, ProjContainer):
                proj.time -= dt
                if proj.time <= 0:
                    for p in proj:
                        p.remove()
                    todelete.append(key)
                for p in proj:
                    u = p.unit
                    m = p.pos + u + u * 50
                    p.update(p.pos.x + u.x * 50, p.pos.y + u.y * 50, m.x, m.y)
        for key in todelete:
            del self.projs[key]

    def draw(self):
        self.batch.draw()

    def correct(self, pos, vel, id):
        self.projs[id].vel = vel
        if (self.projs[id].pos - pos).mag() > 20 * self.scalemag:
            self.projs[id].update(*pos)
        else:
            self.interpolate(id, pos)

    def interpolate(self, id, pos):
        npos = (pos - self.projs[id].pos) * 0.3
        self.projs[id].update(*(self.projs[id].pos + npos))
