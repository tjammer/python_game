import pyglet
from pyglet.gl import *
import parsedae
from animationquat import AnimatedModel


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
    def __init__(self, vertices, faces, normals, material, mode=quads):
        super(Mesh, self).__init__()
        self.vertices = vertices
        self.faces = faces
        self.normals = normals
        self.mode = mode
        self.color = material

    def data_to_batch(self, batch, group=None):
        #outgoing vertices
        self.verts = []
        self.norms = []
        indices = []

        for i, vdata in enumerate(self.faces):
            v, n = vdata
            self.verts.extend(self.vertices[v])
            self.norms.extend(self.normals[n])
            indices.append(i)

        length = len(self.verts) / 3
        self.vertex_list = batch.add_indexed(
            length, self.mode, group,
            indices, *[('v3f/dynamic', self.verts),
                       ('n3f/dynamic', self.norms),
                       ('c4f/static', self.color * length)])


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
            self.meshes.append(Mesh(verts, facearr, norms, color))
        self.tarr = [[None for j in range(len(facedata[i][1])*3)]
                     for i in range(len(facedata))]
        self.add(self.batch)

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

    def draw(self):
        self.batch.draw()
