#!python
#cython: boundscheck=False, wraparound=False, initializedcheck=False, cdivison=True
from libc.stdlib cimport malloc, free
from cython.view cimport array
from libc.math cimport sqrt, sin, cos, copysign
from numpy cimport ndarray, dtype
from shader import vector
from ctypes import c_float


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
    double w
    double x
    double y
    double z


cdef struct Vec4:
    double w
    double x
    double y
    double z


cdef struct Transform:
    Quat q
    Vec4 vec
    int active

transformtype = dtype([('q.w', 'd'), ('q.x', 'd'), ('q.y', 'd'),
                 ('q.z', 'd'), ('vec.w', 'd'), ('vec.x', 'd'),
                 ('vec.y', 'd'), ('vec.z', 'd'), ('active', 'i4')],
                 align=True)

cdef float pih = 1.570796326794


cdef class AnimatedModel:
    #no of vertices, no of faces
    cdef int lv, lf, la
    cdef double scale
    cdef double[:,:] vertices
    cdef double[:,:] normals
    cdef double[:,:] curr_verts
    cdef double[:,:] curr_norms
    cdef int[:,:,:] face_data
    cdef double[:] weights
    cdef double[:,:] times
    cdef int[:] animlen
    cdef int[:] vcounts
    cdef int[:] bone_weight_ids
    cdef int[:] weight_inds
    cdef Transform to_world
    cdef Transform[:] joint_worldData
    cdef Transform[:] joint_currData
    cdef Transform[:] inverse
    cdef Transform[:] skin_matrix
    cdef Transform[:,:,:] keyframes
    cdef Transform *point
    cdef Joint joints
    cdef double[2] pos
    cdef double[3] angles

    def __init__(self, verts, norms, faces, joint_data, joints_, skin_data,
                 anims, scale_):
        cdef int l = len(joint_data), tt, lenanims
        cdef int i, j, k
        self.scale = scale_

        cdef ndarray nparr = ndarray((l,), dtype=transformtype)
        self.joint_worldData = nparr
        cdef Transform * tra
        for i in range(l):
            tra = &self.joint_worldData[i]
            mat4x4_to_transform(joint_data[i], tra)

        nparr = ndarray((l,), dtype=transformtype)
        self.joint_currData = nparr

        l = len(verts)
        self.lv = l
        cyarr = array(shape=(l, 3), itemsize=sizeof(double), format="d")
        self.vertices = cyarr
        for i in range(l):
            for j in range(3):
                self.vertices[i][j] = verts[i][j]

        l = len(verts)
        cyarr = array(shape=(l, 3), itemsize=sizeof(double), format="d")
        self.curr_verts = cyarr
        for i in range(l):
            for j in range(3):
                self.curr_verts[i][j] = 0.

        l = len(norms)
        cyarr = array(shape=(l, 3), itemsize=sizeof(double), format="d")
        self.normals = cyarr
        for i in range(l):
            for j in range(3):
                self.normals[i, j] = norms[i][j]

        l = len(norms)
        cyarr = array(shape=(l, 3), itemsize=sizeof(double), format="d")
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
        cyarr = array(shape=(l,), itemsize=sizeof(double), format="d")
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
        nparr = ndarray((l,), dtype=transformtype)
        self.inverse = nparr
        for i in range(l):
            tra = &self.inverse[i]
            mat4x4_to_transform(inverse_bsm[i], tra)

        self.joints = add(joints_)

        #times for each animation
        l = len(anims)
        tt = max([len(anim[0][0]) for anim in anims])
        cyarr = array(shape=(l, tt), itemsize=sizeof(double), format="d")
        self.times = cyarr
        for i in range(l):
            for j in range(len(anims[i][0][0])):
                self.times[i][j] = anims[i][0][0][j]

        #number of times for each animation
        cyarr = array(shape=(l,), itemsize=sizeof(int), format="i")
        self.animlen = cyarr
        for i in range(l):
            self.animlen[i] = len(anims[i][0][0])

        #transformation data for each animation
        lenanims = len(anims)
        l = len(anims[0])
        nparr = ndarray((lenanims, l, tt), dtype=transformtype)
        self.keyframes = nparr
        for i in range(lenanims):
            for j in range(l):
                for k in range(len(anims[i][j][1])):
                    tra = &self.keyframes[i][j][k]
                    mat4x4_to_transform(anims[i][j][1][k], tra)

        self.la = l
        nparr = ndarray((l,), dtype=transformtype)
        self.skin_matrix = nparr
        self.angles[0] = 0.
        self.angles[2] = -1.570796326794

        #set up bind pose
        self._set_bind_pose(self.joints, 0)
        self._skin_vertices()
        for i in range(self.lv):
            for j in range(3):
                self.vertices[i][j] = self.curr_verts[i][j]


    def get_bindpose(self):
        cdef int i
        transout = [(vector((self.skin_matrix[i].q.x,
                            self.skin_matrix[i].q.y,
                            self.skin_matrix[i].q.z,
                            self.skin_matrix[i].q.w)),
                     vector((self.skin_matrix[i].vec.x,
                            self.skin_matrix[i].vec.y,
                            self.skin_matrix[i].vec.z,
                            self.skin_matrix[i].vec.w)))
                            for i in range(self.la)]
        return zip(*transout)

    #def set_keyframe(self, int direc, pos, double time):
    def set_keyframe(self, float direc, pos, dict weights_, dict times_,
                     dict pikdict, float frc):
        cdef int i, j, k, ln2
        cdef float weight
        cdef double angle
        #set up anim data
        cdef int ln = len(weights_)
        cdef int *indices = <int *>malloc(ln * sizeof(int))
        cdef float *weights = <float *>malloc(ln * sizeof(float))
        cdef float *times = <float *>malloc(ln * sizeof(float))
        for k, (j, weight) in enumerate(weights_.iteritems()):
            indices[k] = j
            weights[k] = weight
            times[k] = times_[j]

        #set up pseudo ik data
        ln2 = len(pikdict)
        cdef PseudoIK *piks = <PseudoIK *>malloc(ln2 * sizeof(PseudoIK))
        for k, (j, angle) in enumerate(pikdict.iteritems()):
            piks[k] = pik_from_dict(j, angle, direc, frc)

        self.pos[0] = <double>pos[0] / self.scale
        self.pos[1] = <double>pos[1] / self.scale
        self.angles[1] = -pih * direc
        self._set_world_matrix(
            self.joints, 0, indices, weights, times, ln, piks, ln2)
        transout = [(vector((self.skin_matrix[i].q.x,
                            self.skin_matrix[i].q.y,
                            self.skin_matrix[i].q.z,
                            self.skin_matrix[i].q.w)),
                     vector((self.skin_matrix[i].vec.x,
                            self.skin_matrix[i].vec.y,
                            self.skin_matrix[i].vec.z,
                            self.skin_matrix[i].vec.w)))
                            for i in range(self.la)]
        free(indices)
        free(weights)
        free(times)
        free(piks)
        return zip(*transout)

    #C functions
    cdef void _set_keyframe(self, int *inds, float *weights, float *times,
                            int ln):
        #self._set_world_matrix(self.joints, 0, time)
        #self._skin_vertices()
        pass

    cdef void _set_world_matrix(
        self, Joint joint, int parent, int *inds, float *weights, float *times,
        int ln, PseudoIK *piks, int ln2):
        cdef int i, j, k, pikind
        cdef float weight
        cdef Timestep ipol
        cdef Transform blended
        cdef Transform *nlerped = <Transform *>malloc(ln * sizeof(Transform))
        cdef Transform test
        #all bones except hip
        if not joint.ind == 0:

            #compute lerped transform for each blended animation
            for i in range(ln):
                ipol = time_frac(
                    times[i], self.times[inds[i]], self.animlen[inds[i]])

                self.point = &nlerped[i]
                nlerp(self.keyframes[inds[i]][joint.ind][ipol.i1],
                  self.keyframes[inds[i]][joint.ind][ipol.i2],
                  ipol.frac,self.point)

            #blend animations
            blended = nlerped[0]
            for i in range(ln-1):
                self.point = &blended
                weight = 0
                for j in range(i+1):
                    weight += weights[j]
                weight = 1 - weight / (weight + weights[i+1])
                nlerp(blended, nlerped[i+1], weight, self.point)

            #test pseudo ik
            pikind = ind_in_pikarr(joint.ind, ln2, piks)
            if pikind != -1:
                self.point = &blended
                trans_mult(blended, piks[pikind].t, self.point)

            self.point = &self.joint_currData[joint.ind]
            trans_mult(self.joint_currData[parent],
                       blended, self.point)
        #hip
        else:
            self.point = &self.to_world
            euler_to_trans(self.angles, self.pos, self.point)

            #compute lerped transform for each blended animation
            for i in range(ln):
                ipol = time_frac(
                    times[i], self.times[inds[i]], self.animlen[inds[i]])

                self.point = &nlerped[i]
                nlerp(self.keyframes[inds[i]][joint.ind][ipol.i1],
                  self.keyframes[inds[i]][joint.ind][ipol.i2],
                  ipol.frac, self.point)

            #blend animations
            blended = nlerped[0]
            for i in range(ln-1):
                self.point = &blended
                weight = 0
                for j in range(i+1):
                    weight += weights[i]
                weight = 1 - weight / (weight + weights[i+1])
                nlerp(blended, nlerped[i+1], weight, self.point)

            self.point = &self.joint_currData[joint.ind]
            trans_mult(self.to_world, blended,
                       self.point)

        #set skinning matrix
        self.point = &self.skin_matrix[joint.ind]
        trans_mult(self.joint_currData[joint.ind],
                   self.inverse[joint.ind], self.point)

        for i in range(joint.len):
            self._set_world_matrix(
                joint.nodes[i], joint.ind, inds, weights, times, ln, piks, ln2)

        free(nlerped)

    cdef void _skin_vertices(self):
        cdef int i, j, jointid
        cdef int o = 0
        cdef double weight
        #this could probably be allocated beforehand
        cyarr = array(shape=(3,), itemsize=sizeof(double), format='d')
        cdef double[:] f3 = cyarr
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
                trans_vector_mult(self.skin_matrix[jointid], self.vertices[i],
                                  f3, weight, self.scale)
                add_memv_f3(self.curr_verts[i], f3)
                #normals
                trans_vector_mult(self.skin_matrix[jointid], self.normals[i],
                                  f3, weight, 0.)
                add_memv_f3(self.curr_norms[i], f3)
            o += self.vcounts[i]

    cdef void _set_bind_pose(self, Joint joint, int parent):
        if not joint.ind == 0:
            self.point = &self.joint_currData[joint.ind]
            trans_mult(self.joint_currData[parent],
                       self.joint_worldData[joint.ind], self.point)
        else:
            self.joint_currData[joint.ind] = self.joint_worldData[joint.ind]

        #set skinning matrix
        self.point = &self.skin_matrix[joint.ind]
        trans_mult(self.joint_currData[joint.ind],
                   self.inverse[joint.ind], self.point)

        cdef int i
        for i in range(joint.len):
            self._set_bind_pose(joint.nodes[i], joint.ind)


cdef void add_memv_f3(double[:] a, double[:] b):
    cdef int i
    for i in range(3):
        a[i] += b[i]


cdef void mat4_mat_3(list m, double mat[3][3]):
    cdef i, j
    for i in range(3):
        for j in range(3):
            mat[j][i] = m[i*4 + j]

#blender
cdef void mat4x4_to_transform(list m, Transform *t):
    cdef double mat[3][3]
    mat4_mat_3(m, mat)
    cdef double tr = (mat[0][0] + mat[1][1] + mat[2][2] + 1.) * 0.25
    cdef double S

    if tr > 0.:
        S = sqrt(tr)
        t.q.w = S
        S = 1. / (4. * S)
        t.q.x = (mat[1][2] - mat[2][1]) * S
        t.q.y = (mat[2][0] - mat[0][2]) * S
        t.q.z = (mat[0][1] - mat[1][0]) * S
    elif mat[0][0] > mat[1][1] and mat[0][0] > mat[2][2]:
        S = sqrt(1. + mat[0][0] - mat[1][1] - mat[2][2]) * 2.
        t.q.x = 0.25 * S
        S = 1. / S
        t.q.w = (mat[1][2] - mat[2][1]) * S
        t.q.y = (mat[1][0] + mat[0][1]) * S
        t.q.z = (mat[2][0] + mat[0][2]) * S
    elif mat[1][1] > mat[2][2]:
        S = sqrt(1. + mat[1][1] - mat[0][0] - mat[2][2]) * 2.
        t.q.y = 0.25 * S
        S = 1. / S
        t.q.w = (mat[1][2] - mat[2][1]) * S
        t.q.x = (mat[1][0] + mat[0][1]) * S
        t.q.z = (mat[2][0] + mat[0][2]) * S
    else:
        S = sqrt(1. + mat[2][2] - mat[0][0] - mat[1][1]) * 2.
        t.q.z = 0.25 * S
        S = 1. / S
        t.q.w = (mat[0][1] - mat[1][0]) * S
        t.q.x = (mat[2][0] + mat[0][2]) * S
        t.q.y = (mat[2][1] + mat[1][2]) * S

    t.vec.w = m[15]
    t.vec.x = m[3]
    t.vec.y = m[7]
    t.vec.z = m[11]


cdef void trans_vector_mult(Transform t, double[:] v, double[:] target,
                            double w, double scale):
    cdef double x = v[0]
    cdef double y = v[1]
    cdef double z = v[2]
    cdef double a = t.q.w * t.q.w
    cdef double b = t.q.x * t.q.x
    cdef double c = t.q.y * t.q.y
    cdef double d = t.q.z * t.q.z
    target[0] = ((a + b - c - d) * x\
               + 2. * t.q.w * t.q.y * z - 2. * t.q.w * t.q.z * y \
               + 2. * t.q.x * t.q.y * y \
               + 2. * t.q.x * t.q.z * z + t.vec.x * scale) * w
    target[1] = ((a - b + c - d) * y\
               + 2. * t.q.w * t.q.z * x + 2. * t.q.y * t.q.x * x \
               + 2. * t.q.y * t.q.z * z \
               - 2. * t.q.w * t.q.x * z + t.vec.y * scale) * w
    target[2] = ((a - b - c + d) * z\
               + 2. * t.q.w * t.q.x * y + 2. * t.q.y * t.q.z * y \
               + 2. * t.q.x * t.q.z * x \
               - 2. * t.q.w * t.q.y * x + t.vec.z * scale) * w


cdef void trans_mult(Transform a, Transform b, Transform *t):
    t.q.w = a.q.w * b.q.w - a.q.x * b.q.x - a.q.y * b.q.y - a.q.z * b.q.z
    t.q.x = a.q.w * b.q.x + a.q.x * b.q.w + a.q.y * b.q.z - a.q.z * b.q.y
    t.q.y = a.q.w * b.q.y - a.q.x * b.q.z + a.q.y * b.q.w + a.q.z * b.q.x
    t.q.z = a.q.w * b.q.z + a.q.x * b.q.y - a.q.y * b.q.x + a.q.z * b.q.w

    cdef double aa = a.q.w * a.q.w
    cdef double bb = a.q.x * a.q.x
    cdef double c = a.q.y * a.q.y
    cdef double d = a.q.z * a.q.z
    t.vec.x = (aa + bb - c - d) * b.vec.x + 2. * a.q.w * a.q.y * b.vec.z \
         - 2. * a.q.w * a.q.z * b.vec.y + 2. * a.q.x * a.q.y * b.vec.y \
         + 2. * a.q.x * a.q.z * b.vec.z + a.vec.x
    t.vec.y = (aa - bb + c - d) * b.vec.y + 2. * a.q.w * a.q.z * b.vec.x \
         + 2. * a.q.y * a.q.x * b.vec.x + 2. * a.q.y * a.q.z * b.vec.z \
         - 2. * a.q.w * a.q.x * b.vec.z + a.vec.y
    t.vec.z = (aa - bb - c + d) * b.vec.z + 2. * a.q.w * a.q.x * b.vec.y \
         + 2. * a.q.y * a.q.z * b.vec.y + 2. * a.q.x * a.q.z * b.vec.x \
         - 2. * a.q.w * a.q.y * b.vec.x + a.vec.z
    t.vec.w = 1.


cdef void euler_to_trans(double[3] angles, double[2] disp, Transform *t):
    cdef double c1 = cos(angles[0] * 0.5)
    cdef double c2 = cos(angles[1] * 0.5)
    cdef double c3 = cos(angles[2] * 0.5)
    cdef double s1 = sin(angles[0] * 0.5)
    cdef double s2 = sin(angles[1] * 0.5)
    cdef double s3 = sin(angles[2] * 0.5)

    t.q.w = c1 * c2 * c3 - s1 * s2 * s3
    t.q.x = s1 * s2 * c3 + c1 * c2 * s3
    t.q.y = s1 * c2 * c3 + c1 * s2 * s3
    t.q.z = c1 * s2 * s3 - s1 * c2 * c3

    t.vec.x = disp[0] + 16 * 2. / 72.
    t.vec.y = disp[1]
    t.vec.z = 0.


cdef axis_to_trans(double axis[3], double angle_, Transform *t):
    cdef double angle = angle_
    cdef double cosangle = cos(angle / 2)
    cdef double sinangle = sin(angle / 2)
    t.q.w = cosangle
    t.q.x = axis[0] * sinangle
    t.q.y = axis[1] * sinangle
    t.q.z = axis[2] * sinangle


cdef void nlerp(Transform a, Transform b, double t, Transform *target):
    cdef double cosangle = a.q.w * b.q.w + a.q.x * b.q.x + a.q.y * b.q.y\
                         + a.q.z * b.q.z
    if cosangle < 0.:
        target.q.w = -a.q.w + t * (b.q.w + a.q.w)
        target.q.x = -a.q.x + t * (b.q.x + a.q.x)
        target.q.y = -a.q.y + t * (b.q.y + a.q.y)
        target.q.z = -a.q.z + t * (b.q.z + a.q.z)
    else:
        target.q.w = a.q.w + t * (b.q.w - a.q.w)
        target.q.x = a.q.x + t * (b.q.x - a.q.x)
        target.q.y = a.q.y + t * (b.q.y - a.q.y)
        target.q.z = a.q.z + t * (b.q.z - a.q.z)

    cdef double norm = sqrt(target.q.w * target.q.w + target.q.x * target.q.x\
                         + target.q.y * target.q.y + target.q.z * target.q.z)
    target.q.w *= 1. / norm
    target.q.x *= 1. / norm
    target.q.y *= 1. / norm
    target.q.z *= 1. / norm

    target.vec.w = a.vec.w + t * (b.vec.w - a.vec.w)
    target.vec.x = a.vec.x + t * (b.vec.x - a.vec.x)
    target.vec.y = a.vec.y + t * (b.vec.y - a.vec.y)
    target.vec.z = a.vec.z + t * (b.vec.z - a.vec.z)


cdef struct Timestep:
    double frac
    #indices for keyframes
    int i1
    int i2


cdef Timestep time_frac(double time, double[:] times, int len_times):
    cdef Timestep ts
    cdef int i
    cdef double diff
    for i in range(len_times):
        if time == times[i]:
            if i == 0:
                ts.frac = 0.
                ts.i1 = 0
                ts.i2 = 1
            else:
                ts.frac = 1.
                ts.i1 = i - 1
                ts.i2 = i
            return ts

        if time > times[i]:
            if i < (len_times - 1) and time < times[i+1]:
                diff = times[i+1] - times[i]
                ts.frac = (time - times[i]) / diff
                ts.i1 = i
                ts.i2 = i + 1
                return ts

    print 'wrong time', time, times
    ts.frac = 1
    ts.i1 = len_times - 2
    ts.i2 = len_times - 1
    return ts


cdef struct PseudoIK:
    int index
    Transform t


cdef normalize(double a[3]):
    cdef double sm = 0
    cdef int i
    for i in range(3):
        sm += a[i] * a[i]
    sm = sqrt(sm)
    for i in range(3):
        a[i] /= sm


cdef PseudoIK pik_from_dict(int key, double angle, float direc, float frac):
    cdef PseudoIK pik
    pik.index = key
    cdef double aangle = abs(angle)
    cdef double axis[3]
    axis[:] = [-(1-abs(frac)), -copysign(frac, frac*direc), 0]
    normalize(axis)
    cdef Transform *p = &pik.t
    axis_to_trans(axis, angle, p)
    return pik


cdef int ind_in_pikarr(int ind, int l, PseudoIK *arr):
    cdef int i
    for i in range(l):
        if ind == arr[i].index:
            return i
    return -1
