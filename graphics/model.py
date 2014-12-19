import pyglet
from pyglet.gl import *
import parsedae
from animationquat import AnimatedModel
from shader import Shader


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
        self.anim = AnimatedModel(*p_data)
        self.meshes = []
        self.batch = pyglet.graphics.Batch()
        for faces in facedata:
            color = faces[0]
            facearr = [(vert, faces[2][i]) for i, vert in enumerate(faces[1])]
            self.meshes.append(Mesh(verts, facearr, norms, color, skn))
        self.tarr = [[None for j in range(len(facedata[i][1])*3)]
                     for i in range(len(facedata))]
        self.add(self.batch)

        self.shader = Shader('skinning')

    def add(self, batch):
        for mesh in self.meshes:
            mesh.data_to_batch(batch)

    def move(self, rottrans, pos):
        self.anim.set_keyframe(rottrans, self.tarr, pos, 2)
        for i, mesh in enumerate(self.meshes):
            mesh.vertex_list.vertices = self.tarr[i]

    def update(self, direction, pos, dt):
        self.anim.set_keyframe(direction, self.tarr, pos, dt)
        for i, mesh in enumerate(self.meshes):
            mesh.vertex_list.vertices = self.tarr[i]

    def draw(self, mvp):
        self.shader.set('mvp', mvp)
        with self.shader:
            self.batch.draw()
