#!python
#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivison=True
from libc.stdlib cimport malloc, free
from cython.view cimport array
from libc.math cimport sqrt
from numpy cimport ndarray, dtype

cdef struct Joint:
    int ind
    int len
    Joint *nodes

cdef Joint add(object joint_):
    cdef Joint joint
    joint.ind = joint_.index
    joint.len = joint_.len
    joint.nodes = <Joint *>malloc(joint.len * sizeof(Joint))
    for i in range(joint.len):
        joint.nodes[i] = add(joint_.nodes[i])
    return joint

cdef struct Quat:
    float w
    float x
    float y
    float z

cdef Quat gen_quat():
    cdef Quat q
    q.w = q.x = q.y = q.z = 0
    return q

cdef struct Vec4:
    float w
    float x
    float y
    float z

cdef Vec4 gen_vec4():
    cdef Vec4 v
    v.w = v.x = v.y = v.z = 0
    return v

cdef struct Transform:
    Quat quat
    Vec4 vec
    int active

transformtype = [('quat.w', 'f4'), ('quat.x', 'f4'), ('quat.y', 'f4'),
                 ('quat.z', 'f4'), ('vec.w', 'f4'), ('vec.x', 'f4'),
                 ('vec.y', 'f4'), ('vec.z', 'f4'), ('active', 'i4')]


cdef class AnimatedModel:
    #no of vertices, no of faces
    cdef int lv, lf
    cdef float scale
    cdef float[:,:] vertices
    cdef float[:,:] normals
    cdef float[:,:] curr_verts
    cdef float[:,:] curr_norms
    cdef int[:,:,:] face_data
    cdef float[:,:] joint_worldData
    cdef float[:,:] joint_currData
    cdef float[:] weights
    cdef float[:,:] times
    cdef float[:,:,:] keyframes
    cdef int[:] vcounts
    cdef int[:] bone_weight_ids
    cdef int[:] weight_inds
    cdef float[:,:] inverse
    cdef float[:,:] skin_matrix
    cdef Joint joints

    def __init__(self, verts, norms, faces, joint_data, joints_, skin_data,
                 anims, scale_):
        cdef int l = len(joint_data), tt
        cdef int i, j, k
        self.scale = scale_
        cdef ndarray abab = ndarray((l,), dtype=_dtype)
        cdef Transform[:] unity = abab

        cyarr = array(shape=(l, 16), itemsize=sizeof(float), format="f")
        self.joint_worldData = cyarr
        for i in range(l):
            for j in range(16):
              self.joint_worldData[i][j] = joint_data[i][j]

        cyarr = array(shape=(l, 16), itemsize=sizeof(float), format="f")
        self.joint_currData = cyarr

        l = len(verts)
        self.lv = l
        cyarr = array(shape=(l, 3), itemsize=sizeof(float), format="f")
        self.vertices = cyarr
        for i in range(l):
            for j in range(3):
                self.vertices[i][j] = verts[i][j]

        l = len(verts)
        cyarr = array(shape=(l, 3), itemsize=sizeof(float), format="f")
        self.curr_verts = cyarr
        for i in range(l):
            for j in range(3):
                self.curr_verts[i][j] = 0.

        l = len(norms)
        cyarr = array(shape=(l, 3), itemsize=sizeof(float), format="f")
        self.normals = cyarr
        for i in range(l):
            for j in range(3):
                self.normals[i, j] = norms[i][j]

        l = len(norms)
        cyarr = array(shape=(l, 3), itemsize=sizeof(float), format="f")
        self.curr_norms = cyarr

        l = len(faces)
        self.lf = l
        tt = max(len(fc[1]) for fc in faces)
        cyarr = array(shape=(l, 3, tt), itemsize=sizeof(int), format="i")
        self.face_data = cyarr
        for i in range(l):
            self.face_data[i][0][0] = len(faces[i][1])
            for j in range(self.face_data[i][0][0]):
                self.face_data[i][1][j] = faces[i][1][j]
                self.face_data[i][2][j] = faces[i][2][j]

        skin_weights, vcount, bone_w, w_inds, inverse_bsm = skin_data

        l = len(skin_weights)
        cyarr = array(shape=(l,), itemsize=sizeof(float), format="f")
        self.weights = cyarr
        for i in range(l):
            self.weights[i] = skin_weights[i]

        l = len(vcount)
        cyarr = array(shape=(l,), itemsize=sizeof(int), format="i")
        self.vcounts = cyarr
        for i in range(l):
            self.vcounts[i] = vcount[i]

        l = len(bone_w)
        cyarr = array(shape=(l,), itemsize=sizeof(int), format="i")
        self.bone_weight_ids = cyarr
        for i in range(l):
            self.bone_weight_ids[i] = bone_w[i]

        l = len(w_inds)
        cyarr = array(shape=(l,), itemsize=sizeof(int), format="i")
        self.weight_inds = cyarr
        for i in range(l):
            self.weight_inds[i] = w_inds[i]

        l = len(inverse_bsm)
        cyarr = array(shape=(l, 16), itemsize=sizeof(float), format="f")
        self.inverse = cyarr
        for i in range(l):
            for j in range(16):
                self.inverse[i][j] = inverse_bsm[i][j]

        self.joints = add(joints_)

        l = len(anims)
        tt = len(anims[0][0])
        cyarr = array(shape=(l, tt), itemsize=sizeof(float), format="f")
        self.times = cyarr
        for i in range(l):
            for j in range(tt):
                self.times[i][j] = anims[i][0][j]

        l = len(anims)
        cyarr = array(shape=(l, tt, 16), itemsize=sizeof(float), format='f')
        self.keyframes = cyarr
        for i in range(l):
            for j in range(tt):
                for k in range(16):
                    self.keyframes[i][j][k] = anims[i][1][j][k]

        cyarr = array(shape=(l, 16), itemsize=sizeof(float), format='f')
        self.skin_matrix = cyarr

        #set up bind pose
        self._set_bind_pose(self.joints, 0)
        self._skin_vertices()
        for i in range(self.lv):
            for j in range(3):
                self.vertices[i][j] = self.curr_verts[i][j]


    def set_keyframe(self, int i, lst):
        cdef int j, k
        self._set_keyframe(i)
        for i in range(self.lf):
            for j in range(self.face_data[i][0][0]):
                for k in range(3):
                    lst[i][j*3+k] = self.curr_verts[self.face_data[i][1][j]][k]

    def get_stuff(self, lst):
        cdef int i, j, k
        for i in range(self.lf):
            for j in range(self.face_data[i][0][0]):
                for k in range(3):
                    lst[i][j*3+k] = self.curr_verts[self.face_data[i][1][j]][k]


    #C functions
    cdef void _set_keyframe(self, int i):
        self._set_world_matrix(self.joints, 0, i)
        self._skin_vertices()

    cdef void _set_world_matrix(self, Joint joint, int parent, int time):
        if not joint.ind == 0:
            matrix_mult(self.joint_currData[parent],
                        self.keyframes[joint.ind][time],
                        self.joint_currData[joint.ind])
        else:
            self.joint_currData[joint.ind] = self.keyframes[joint.ind][time]

        #set skinning matrix
        matrix_mult(self.joint_currData[joint.ind],
                    self.inverse[joint.ind], self.skin_matrix[joint.ind])

        cdef int i
        for i in range(joint.len):
            self._set_world_matrix(joint.nodes[i], joint.ind, time)

    cdef void _skin_vertices(self):
        cdef int i, j, jointid
        cdef int o = 0
        cdef float weight
        #this could probably be allocated beforehand
        cyarr = array(shape=(3,), itemsize=sizeof(float), format='f')
        cdef float[:] f3 = cyarr
        for i in range(self.lv):
            self.curr_verts[i][0] = 0.
            self.curr_verts[i][1] = 0.
            self.curr_verts[i][2] = 0.
            self.curr_norms[i][0] = 0.
            self.curr_norms[i][1] = 0.
            self.curr_norms[i][2] = 0.
            for j in range(self.vcounts[i]):
                jointid = self.bone_weight_ids[o + j]
                weight = self.weights[self.weight_inds[o + j]]
                #vertices
                matrix_vector_mult(self.skin_matrix[jointid],
                                   self.vertices[i], f3, weight, self.scale)
                add_memv_f3(self.curr_verts[i], f3)
                #normals
                matrix_vector_mult(self.skin_matrix[jointid],
                                   self.normals[i], f3, weight, 0.)
                add_memv_f3(self.curr_norms[i], f3)
            o += self.vcounts[i]

    cdef void _set_bind_pose(self, Joint joint, int parent):
        if not joint.ind == 0:
            matrix_mult(self.joint_currData[parent],
                        self.joint_worldData[joint.ind],
                        self.joint_currData[joint.ind])
        else:
            self.joint_currData[joint.ind] = self.joint_worldData[joint.ind]
        #set skinning matrix
        matrix_mult(self.joint_currData[joint.ind],
                    self.inverse[joint.ind], self.skin_matrix[joint.ind])
        cdef int i
        for i in range(joint.len):
            self._set_bind_pose(joint.nodes[i], joint.ind)

cdef void matrix_mult(float[:] a, float[:] b, float[:] target):
    cdef int i, j
    for i in range(0, 16, 4):
        for j in range(4):
            target[i + j] = a[i + 0] * b[j + 0] \
                          + a[i + 1] * b[j + 4] \
                          + a[i + 2] * b[j + 8] \
                          + a[i + 3] * b[j + 12]


cdef void matrix_vector_mult(float[:] a, float[:] v, float[:] t, float w,
                             float scale):
    cdef int i
    for i in range(3):
            t[i] = (a[i*4 + 0] * v[0] + a[i*4 + 1] * v[1] \
                 +  a[i*4 + 2] * v[2] + a[i*4 + 3] * scale) * w

cdef void add_memv_f3(float[:] a, float[:] b):
    cdef int i
    for i in range(3):
        a[i] += b[i]

cdef Transform gen_transform(int active):
    cdef Transform trans
    trans.quat = gen_quat()
    trans.vec = gen_vec4()
    trans.active = active
    return trans

cdef void mat4x4_to_quat_transl(float[:] m, Quat *q, Vec4 *tv):
    cdef float tr = m[0] + m[5] + m[10]
    cdef float S
    """ 0, 1, 2, 3      m00 m01 m02
        4, 5, 6, 7      m10 m11 m12
        8, 9, 10, 11    m20 m21 m22"""

    if tr > 0:
        S = sqrt(tr + 1.) * 2
        q.w = 0.25 * S
        q.x = (m[9] - m[6]) / S
        q.y = (m[2] - m[8]) / S
        q.z = (m[4] - m[1]) / S
    elif m[0] > m[5] and m[0] > m[10]:
        S = sqrt(1. + m[0] - m[5] - m[10]) * 2
        q.w = (m[9] - m[6]) / S
        q.x = 0.25 * S
        q.y = (m[1] + m[4]) / S
        q.z = (m[2] + m[8]) / S
    elif m[5] > m[10]:
        S = sqrt(1. + m[5] - m[0] - m[10]) * 2
        q.w = (m[2] - m[8]) / S
        q.x = (m[1] + m[4]) / S
        q.y = 0.25 * S
        q.z = (m[6] + m[9]) / S
    else:
        S = sqrt(1. + m[10] - m[0] - m[5]) * 2
        q.w = (m[4] - m[1]) / S
        q.x = (m[2] + m[8]) / S
        q.y = (m[6] + m[9]) / S
        q.z = 0.25 * S

    tv.w = m[15]
    tv.x = m[3]
    tv.y = m[7]
    tv.z = m[11]

cdef void quat_trans_to_mat4x4(Quat *q, Vec4 *tv, float[:] m):

    m[0] = 1. - 2 * q.y * q.y - 2 * q.z * q.z
    m[1] = 2 * q.x * q.y - 2 * q.z * q.w
    m[2] = 2 * q.x * q.z + 2 * q.y * q.w
    m[3] = tv.x
    m[4] = 2 * q.x * q.y + 2 * q.z * q.w
    m[5] = 1. - 2 * q.x * q.x - 2 * q.z * q.z
    m[6] = 2 * q.y * q.z - 2 * q.x * q.w
    m[7] = tv.y
    m[8] = 2 * q.x * q.z - 2 * q.y * q.w
    m[9] = 2 * q.y * q.z + 2 * q.x * q.w
    m[10] = 1. - 2 * q.x * q.x - 2 * q.y * q.y
    m[11] = tv.z
    m[12] = 0.
    m[13] = 0.
    m[14] = 0.
    m[15] = tv.w


cdef void quat_vector_mult(Quat *q, Vec4 *tv, float[:] v, float[:] t):
    cdef float x = v[0]
    cdef float y = v[1]
    cdef float z = v[2]
    cdef float a = q.w * q.w
    cdef float b = q.x * q.x
    cdef float c = q.y * q.y
    cdef float d = q.z * q.z
    t[0] = (a + b - c - d) * x\
           + 2. * q.w * q.y * z - 2. * q.w * q.z * y + 2. * q.x * q.y * y \
           + 2. * q.x * q.z * z + tv.x
    t[1] = (a - b + c - d) * y\
           + 2. * q.w * q.z * x + 2. * q.y * q.x * x + 2. * q.y * q.z * z \
           - 2. * q.w * q.x * z + tv.y
    t[2] = (a - b - c + d) * z\
           + 2. * q.w * q.x * y + 2. * q.y * q.z * y + 2. * q.x * q.z * x \
           - 2. * q.w * q.y * x + tv.z

cdef void quat_mult(Quat *a, Quat *b, Quat *t, Vec4 *av, Vec4 *bv, Vec4 *tv):
    t.w = a.w * b.w - a.x * b.x - a.y * b.y - a.z * b.z
    t.x = a.w * b.x + a.x * b.w + a.y * b.z - a.z * b.y
    t.y = a.w * b.y - a.x * b.z + a.y * b.w + a.z * b.x
    t.z = a.w * b.z + a.x * b.y - a.y * b.x + a.z * b.w

    cdef float aa = a.w * a.w
    cdef float bb = a.x * a.x
    cdef float c = a.y * a.y
    cdef float d = a.z * a.z
    tv.x = (aa + bb - c - d) * bv.x + 2. * a.w * a.y * bv.z \
         - 2. * a.w * a.z * bv.y + 2. * a.x * a.y * bv.y \
         + 2. * a.x * a.z * bv.z + av.x
    tv.y = (aa - bb + c - d) * bv.y + 2. * a.w * a.z * bv.x \
         + 2. * a.y * a.x * bv.x + 2. * a.y * a.z * bv.z \
         - 2. * a.w * a.x * bv.z + av.y
    tv.z = (aa - bb - c + d) * bv.z + 2. * a.w * a.x * bv.y \
         + 2. * a.y * a.z * bv.y + 2. * a.x * a.z * bv.x \
         - 2. * a.w * a.y * bv.x + av.z
    tv.w = 1.

def quattest(matrix, matrix2, matrix3):
    cyarr = array(shape=(16,), itemsize=sizeof(float), format='f')
    cdef float[:] cmat = cyarr
    cdef int i
    for i in range(16):
        cmat[i] = matrix[i]
    cyarr = array(shape=(16,), itemsize=sizeof(float), format='f')
    cdef float[:] mat1 = cyarr
    for i in range(16):
        mat1[i] = 0.
    cyarr = array(shape=(16,), itemsize=sizeof(float), format='f')
    cdef float[:] cmat2 = cyarr
    for i in range(16):
        cmat2[i] = matrix2[i]
    cyarr = array(shape=(16,), itemsize=sizeof(float), format='f')
    cdef float[:] out2 = cyarr
    for i in range(16):
        out2[i] = 0
    cyarr = array(shape=(16,), itemsize=sizeof(float), format='f')
    cdef float[:] cmat3 = cyarr
    for i in range(16):
        cmat3[i] = matrix3[i]
    cyarr = array(shape=(16,), itemsize=sizeof(float), format='f')
    cdef float[:] cmat3out = cyarr
    for i in range(16):
        cmat3out[i] = 0

    cdef Quat MAT2 = gen_quat()
    cdef Quat *mat2 = &MAT2
    cdef Vec4 VEC2 = gen_vec4()
    cdef Vec4 *vec2 = &VEC2

    cdef Quat MAT3 = gen_quat()
    cdef Quat *mat3 = &MAT3
    cdef Vec4 VEC3 = gen_vec4()
    cdef Vec4 *vec3 = &VEC3

    cdef Quat Q = gen_quat()
    cdef Vec4 TV = gen_vec4()
    cdef Quat *q = &Q
    cdef Vec4 *tv = &TV

    cdef Quat Q3 = gen_quat()
    cdef Vec4 TV3 = gen_vec4()
    cdef Quat *q3 = &Q3
    cdef Vec4 *tv3 = &TV3

    cdef Quat Q2 = gen_quat()
    cdef Vec4 TV2 = gen_vec4()
    cdef Quat *q2 = &Q2
    cdef Vec4 *tv2 = &TV2
    mat4x4_to_quat_transl(cmat, q, tv)
    mat4x4_to_quat_transl(cmat2, q2, tv2)
    mat4x4_to_quat_transl(cmat3, q3, tv3)
    matrix_mult(cmat, cmat2, mat1)
    matrix_mult(mat1, cmat3, cmat3out)
    quat_mult(q, q2, mat2, tv, tv2, vec2)
    quat_mult(mat2, q3, mat3, vec2, tv3, vec3)
    quat_trans_to_mat4x4(mat3, vec3, out2)

    for i in range(16):
        matrix[i] = cmat3out[i]
        matrix2[i] = out2[i]
