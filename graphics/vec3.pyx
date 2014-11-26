from libc.math cimport sqrt

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

    def __richcmp__(self, other, int op):
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
