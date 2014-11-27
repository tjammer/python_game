import pyglet
from pyglet.gl import *
from os.path import abspath
import sys
sys.path.append('/home/jammer/Documents/python_game/graphics/')
from shader import OffscreenBuffer as fbo
from vec3 import rotate_translate


def load_obj_file(filename):
    """loads the simplest .obj file with faces without normals"""
    filename = abspath(filename)
    vertices = []
    faces = []
    normals = []
    material_name = None
    libname = None

    #(face, material_name)
    facegroups = []

    for line in open(filename, 'r'):
        if line.startswith('#'):
            continue

        elif line.startswith('v '):
            vertices.append(map(process, line.split()[1:]))

        elif line.startswith('vn'):
            normals.append(map(float, line.split()[1:]))

        elif line.startswith('f'):
            item = line.split()[1:]
            faces.append(zip(*[map(int, pack.split('//')) for pack in item]))

        elif line.startswith('usemtl'):
            if faces and material_name:
                facegroups.append((faces, material_name))
                faces = []
            material_name = line.split()[1]

        elif line.startswith('mtllib'):
            lib = line.split()[1]
            libname = filename[:filename.rindex('/')] + '/' + lib

    if faces and material_name:
        facegroups.append((faces, material_name))

    #return vertices, faces, normals
    meshes = []
    for faces, material_name in facegroups:
        material = load_material(libname, material_name)
        meshes.append(Mesh(
            vertices, faces, normals, material))

    return meshes


def process(str):
    return float(str) * 270


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
        self.color = material + (1.0,)

    def data_to_batch(self, batch, group=None):
        #outgoing vertices
        self.verts = []
        self.norms = []
        indices = []

        #list containing already seen vertices
        processed = {}
        count = 0

        for vdata in (vdata for face in self.faces for vdata in zip(*face)):
            v, n = vdata

            try:
                i = processed[vdata]
            except KeyError:
                i = count
                count += 1
                processed[vdata] = i
                self.verts.extend(self.vertices[v - 1])
                self.norms.extend(self.normals[n - 1])
            indices.append(i)

        print len(self.verts)
        length = len(self.verts) / 3
        self.vertex_list = batch.add_indexed(
            length, self.mode, group,
            indices, *[('v3f/dynamic', self.verts), ('n3f/dynamic', self.norms),
                       ('c4f/static', self.color * length)])


class Model(object):
    """docstring for Model"""
    def __init__(self, filename):
        super(Model, self).__init__()
        self.meshes = load_obj_file(filename)

    def add(self, batch):
        for mesh in self.meshes:
            mesh.data_to_batch(batch)

    def move(self, rottrans):
        #rottrans: (angle, ux, uy, uz, dx, dy, dz)
        for mesh in self.meshes:
            mesh.verts = rotate_translate(mesh.verts, *rottrans)
            mesh.norms = rotate_translate(mesh.norms,
                                          *(rottrans[:4] + [0, 0, 0]))
            mesh.vertex_list.vertices = mesh.verts
            mesh.vertex_list.normals = mesh.norms
