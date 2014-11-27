from libc.math cimport sqrt, sin, cos, acos
cimport cython
from libc.stdlib cimport malloc, free

cdef class vec3:
    cdef public float x, y, z

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __repr__(self):
        return ', '.join((str(self.x), str(self.y), str(self.z)))

    def __sub__(self, vec):
        if isinstance(vec, vec3):
            return vec3(self.x - vec.x, self.y - vec.y, self.z - vec.z)
        else:
            raise TypeError

    def __add__(self, vec):
        if isinstance(vec, vec3):
            return vec3(self.x + vec.x, self.y + vec.y, self.z + vec.z)
        else:
            raise TypeError

    def __mul__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return vec3(self.x * num, self.y * num, self.z * num)
        else:
            raise TypeError

    def __div__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return vec3(self.x / num, self.y / num, self.z / num)
        else:
            raise TypeError

    def __richcmp__(self, vec3 other, int op):
        if isinstance(other, vec3):
            if op == 2:
                if other.x == self.x:
                    if other.y == self.y:
                        if other.z == self.z:
                            return True
                return False
            elif op == 3:
                if other.x == self.x:
                    if other.y == self.y:
                        if other.z == self.z:
                            return False
                return True
            else:
                raise TypeError
        else:
            raise TypeError

    def mag(self):
        """magnitude of the vector"""
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        mag = self.mag()
        if not mag == 0.:
            return self / mag
        else:
            return vec3(0., 0., 0.)


def rotate_translate(object arr, float angle, float l, float m, float n,
                     float dx, float dy, float dz):
    #lmn is the unit vector of the rotation axis, angle the angle in degree,
    #dxyz is the offset for translation

    #angle in radians
    cdef float theta = angle * acos(0.) / 90.

    #convert python list to c array
    cdef float *carr
    cdef int length = len(arr)

    carr = <float *> malloc(length * cython.sizeof(float))
    if carr is NULL:
        raise MemoryError

    cdef int i
    for i in xrange(length):
        carr[i] = arr[i]

    #set up factors for rotation
    cdef float c = cos(theta)
    cdef float s = sin(theta)
    """[A, B, C]
       [D, E, F]
       [G, H, I]"""
    cdef float A = l * l * (1. - c) + c
    cdef float B = l * m * (1. - c) - n * s
    cdef float C = l * n * (1. - c) + m * s
    cdef float D = m * l * (1. - c) + n * s
    cdef float E = m * m * (1. - c) + c
    cdef float F = n * m * (1. - c) - l * s
    cdef float G = l * n * (1. - c) - m * s
    cdef float H = m * n * (1. - c) + l * s
    cdef float I = n * n * (1. - c) + c

    #arr consists of l / 3 vectors
    cdef float x, y, z

    for i in xrange(length / 3):
        x = carr[i*3]
        y = carr[i*3+1]
        z = carr[i*3+2]
        #do the rotation and add the translation
        carr[i*3] = A * x + B * y + C * z + dx
        carr[i*3+1] = D * x + E * y + F * z + dy
        carr[i*3+2] = G * x + H * y + I * z + dz

    #return arr back to python array
    for i in xrange(length):
        arr[i] = carr[i]
    free(carr)
    return arr
