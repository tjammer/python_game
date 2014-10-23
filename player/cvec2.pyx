from libc.math cimport sqrt

cdef class cvec2:
    cdef public float x, y

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    def __repr__(self):
        return ', '.join((str(self.x), str(self.y)))

    def __sub__(self, vec):
        if isinstance(vec, cvec2):
            return cvec2(self.x - vec.x, self.y - vec.y)
        else:
            raise TypeError

    def __add__(self, vec):
        if isinstance(vec, cvec2):
            return cvec2(self.x + vec.x, self.y + vec.y)
        else:
            raise TypeError

    def __mul__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return cvec2(self.x * num, self.y * num)
        elif isinstance(num, cvec2):
            return cvec2(self.x * num.x, self.y * num.y)

    def __div__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return cvec2(self.x / num, self.y / num)
        else:
            raise TypeError

    def __richcmp__(self, other, int op):
        if isinstance(other, cvec2):
            if op == 2:
                if other.x == self.x:
                    if other.y == self.y:
                        return True
                return False
            elif op == 3:
                if other.x == self.x:
                    if other.y == self.y:
                        return False
                return True
            else:
                raise TypeError
        else:
            raise TypeError

    def __pow__(self, num, mod):
        return cvec2(self.x * self.x, self.y * self.y)

    def mag(self):
        """magnitude of the vector"""
        return sqrt(self.x * self.x + self.y * self.y)
