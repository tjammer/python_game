import pyglet
from pyglet.gl import *
import parsedae
from animationquat import AnimatedModel
from shader import Shader
from math import copysign


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
            indices, *[('v3f/dynamic', self.verts),
                       ('n3f/dynamic', self.norms),
                       ('c4f/static', self.color * length),
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
conditions = {0: 'onGround', 1: 'onGround'}


class AnimationUpdater(object):
    """docstring for AnimationUpdater"""
    def __init__(self, animdata, animator):
        super(AnimationUpdater, self).__init__()
        self.animdata = animdata
        self.metas = []
        for i, ad in enumerate(animdata):
            times, mats = ad[0]
            self.metas.append(MetaAnimation(i, max(times)))
        self.animator = animator
        self.weights = {}
        self.times = {}

    def __iter__(self):
        return iter(self.weights)

    def update(self, dt, state):
        #if state.conds.onGround:
        direc = copysign(1, state.vel.x)
        for meta in self.metas:
            meta.update(dt, state.conds, self.weights, self.times)

        #specials
        avel = abs(state.vel.x)
        if state.conds.onGround:
            self.weights[0] = min(1., avel / 480.)
            self.weights[1] = max(0., 1 - avel / 480)
            """if not 1 in self.times:
                self.times[1] = 0.
            else:
                self.times[1] += dt"""
        else:
            """if 1 in self.times:
                del self.times[1]
                del self.weights[1]"""

        #normalize weights
        norm = sum(w for w in self.weights.values())
        for key, val in self.weights.iteritems():
            self.weights[key] = val / norm

        pos = state.pos
        quats, verts = self.animator.set_keyframe(direc, pos, self.weights,
                                                  self.times)
        return quats, verts


timescales = {0: 2.8, 1: 1}


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
        self.faderate = 2.

    def update(self, dt, conds, weights, times):
        if conds.__getattribute__(conditions[self.index]):
            self.activate(dt)
            self.timer += dt * self.timescale
            if self.timer >= self.maxtime:
                while self.timer >= self.maxtime:
                    self.timer -= self.maxtime

            weights[self.index] = self.weight
            times[self.index] = self.timer

        else:
            self.deactivate(dt, weights, times)

    def activate(self, dt):
        self.active = True
        if self.weight < 1.:
            self.weight += dt * self.faderate
            if self.weight >= 1.:
                self.weight = 1.

    def deactivate(self, dt, weights, times):
        self.active = False
        self.timer = 0.
        if self.weight:
            self.weight -= dt * self.faderate
            if self.weight <= 0.:
                self.weight = 0
                del weights[self.index]
                del times[self.index]
