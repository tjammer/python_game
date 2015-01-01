import pyglet
from pyglet.gl import *
import parsedae
from animationquat import AnimatedModel
from shader import Shader
from math import copysign, acos


def load_material(libname, material_name):
    blockname = None

    for line in open(libname, 'r'):
        if line.startswith('newmtl'):
            blockname = line.split()[1]
        elif line.startswith('Kd') and blockname == material_name:
            return tuple(map(float, line.split()[1:]))

    return False

quads = pyglet.graphics.GL_QUADS


class Mesh(object):
    """docstring for Mesh"""
    def __init__(self, vertices, faces, normals, material, skind, mode=quads):
        super(Mesh, self).__init__()
        self.vertices = vertices
        self.faces = faces
        self.normals = normals
        self.mode = mode
        self.color = material
        self.skin_data = skind

    def data_to_batch(self, batch, group=None):
        #extract skin data
        skin_weights, vcount, bone_id, weight_inds, inv = self.skin_data
        #set up lists for vertex skinning data
        weights_ = []
        w_lens_ = []
        w_bone_ids_ = []
        #index for weights
        w_ind = 0
        for i, vc in enumerate(vcount):
            w_lens_.append(vc)
            weights_.append([skin_weights[j]
                            for j in weight_inds[w_ind:w_ind+vc]])
            w_bone_ids_.append(bone_id[w_ind:w_ind+vc])
            w_ind += vc

        #outgoing vertices
        self.verts = []
        self.norms = []
        indices = []
        #outgoing skin data
        weights = []
        w_lens = []
        w_bone_ids = []

        for i, vdata in enumerate(self.faces):
            v, n = vdata
            self.verts.extend(self.vertices[v])
            self.norms.extend(self.normals[n])
            indices.append(i)
            assert vcount[v] < 5
            cts = vcount[v]
            w_lens.append(cts)
            weights.extend(weights_[v] + [0] * (4 - cts))
            w_bone_ids.extend(w_bone_ids_[v] + [0] * (4 - cts))

        length = len(self.verts) / 3
        self.vertex_list = batch.add_indexed(
            length, self.mode, group,
            indices, *[('0g3f/stream', self.verts),
                       ('1g3f/stream', self.norms),
                       ('2g4f/static', self.color * length),
                       ('3g4f/static', weights), ('4g1i/static', w_lens),
                       ('5g4i/static', w_bone_ids)])


class Model(object):
    """docstring for Model"""
    def __init__(self, filename, scale):
        super(Model, self).__init__()
        p_data = parsedae.parse_dae(filename, scale)
        verts, norms, facedata, jd, js, skn, anm, fsc = p_data
        self.maxtime = max(anm[0][0])
        _anim = AnimatedModel(*p_data)
        self.anim = AnimationUpdater(anm, _anim)
        self.meshes = []
        self.batch = pyglet.graphics.Batch()
        for faces in facedata:
            color = faces[0]
            facearr = [(vert, faces[2][i]) for i, vert in enumerate(faces[1])]
            self.meshes.append(Mesh(verts, facearr, norms, color, skn))
        self.tarr = [[None for j in range(len(facedata[i][1])*3)]
                     for i in range(len(facedata))]
        self.add(self.batch)
        self.quats, self.vecs = _anim.get_bindpose()
        self.shader = Shader('skinning')
        self.shader.set('quats', self.quats)
        self.shader.set('vecs', self.vecs)
        self.shader.set('scale', fsc)

    def add(self, batch):
        for mesh in self.meshes:
            mesh.data_to_batch(batch)

    def update(self, dt, state):
        self.quats, self.vecs = self.anim.update(dt, state)
        self.shader.set('quats', self.quats)
        self.shader.set('vecs', self.vecs)

    def draw(self, mvp):
        self.shader.set('mvp', mvp)
        with self.shader:
            self.batch.draw()

animations = {'run': 0, 'stand': 1}
conditions = {0: ('onGround',), 1: ('onGround',),
              2: ('ascending', 'onRightWall', 'onLeftWall'),
              3: ('descending',), 4: ('landing',)}
timescales = {0: 3, 1: 1, 2: 2, 3: 2.5, 4: 1, 5: 1.5, 6: 1.3}
loops = {0: 1, 1: 1, 2: 0, 3: 0, 4: 0}


class AnimationUpdater(object):
    """docstring for AnimationUpdater"""
    def __init__(self, animdata, animator):
        super(AnimationUpdater, self).__init__()
        self.animdata = animdata
        self.metas = []
        for i, ad in enumerate(animdata):
            if i in conditions:
                times, mats = ad[0]
                self.metas.append(MetaAnimation(i, max(times)))
        self.metas[3].fadeoutrate = 8.
        self.metas[4].fadeinrate = 8.
        self.animator = animator
        self.weights = {}
        self.times = {}
        #for direction
        self.t = 0
        self.dir = 1.

    def __iter__(self):
        return iter(self.weights)

    def update(self, dt, state):
        #if state.conds.onGround:
        self.set_dir(dt, state)
        for meta in self.metas:
            meta.update(dt, state.conds, self.weights, self.times)

        #specials
        avel = abs(state.vel.x)
        if state.conds.onGround:
            self.weights[animations['run']] *= min(1., avel / 480.)
            if not 4 in self.weights:
                self.weights[animations['stand']] *= max(0., 1 - avel / 480.)

        #normalize weights
        norm = sum(w for w in self.weights.values())
        for key, val in self.weights.iteritems():
            self.weights[key] = val / norm

        state.mpos.x *= copysign(1, self.dir)
        cosangle = state.mpos.normalize()
        angle = copysign(acos(cosangle.x), cosangle.y)
        frc = angle / 3.1415926535897
        pikdict = {1: angle / 6, 2: angle / 3, 3: angle / 2}
        quats, verts = self.animator.set_keyframe(
            self.dir, state.pos, self.weights, self.times, pikdict, frc)
        return quats, verts

    def set_dir(self, dt, state):
        if state.vel.x != 0:
            self.t -= (self.t - copysign(1, state.vel.x)) * 11. * dt
            self.dir = easeout(self.t + 1, -1, 2, 2)
        else:
            if state.conds.onRightWall:
                self.dir = 1.
            elif state.conds.onLeftWall:
                self.dir = -1.
            else:
                self.t -= (self.t - copysign(1, self.dir)) * 11. * dt
                self.dir = easeout(self.t + 1, -1, 2, 2)


class MetaAnimation(object):
    """docstring for MetaAnimation"""
    def __init__(self, index, maxtime):
        super(MetaAnimation, self).__init__()
        self.index = index
        self.timer = 0.
        self.maxtime = maxtime
        self.active = False
        self.timescale = timescales[index]

        self.weight = 0.
        self.fadeinrate = 4.
        self.fadeoutrate = 4.

    def update(self, dt, conds, weights, times, force=False):
        if (True in (conds.__getattribute__(c) for c in conditions[self.index])
           or force):
            self.activate(dt)
            self._step(dt)
            if force:
                self._step(dt)

            weights[self.index] = self.weight
            times[self.index] = self.timer

        else:
            self.deactivate(dt, weights, times)

    def activate(self, dt):
        self.active = True
        if self.weight < 1.:
            self.weight += dt * self.fadeinrate
            if self.weight >= 1.:
                self.weight = 1.

    def deactivate(self, dt, weights, times):
        self.active = False
        if self.weight:
            self.weight -= dt * self.fadeoutrate
            self._step(dt)
            weights[self.index] = self.weight
            times[self.index] = self.timer

            if self.weight <= 0.:
                self.weight = 0
                del weights[self.index]
                del times[self.index]
                self.timer = 0.

    def _step(self, dt, pos=True):
        if pos:
            self.timer += dt * self.timescale
            if self.timer >= self.maxtime:
                while self.timer >= self.maxtime:
                    if loops[self.index]:
                        self.timer -= self.maxtime
                    else:
                        self.timer = self.maxtime - dt
        else:
            self.timer -= dt * self.timescale
            if self.timer <= 0.:
                while self.timer <= 0.:
                    self.timer += 0.


def easeout(t, b, c, d):
    t /= d
    return -c * t * (t-2) + b
