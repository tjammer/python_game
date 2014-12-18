from libc.math cimport sqrt

cdef class cvec2:

    def __init__(self, float x, float y):
        self.x = x
        self.y = y

    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, int key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError

    def __setitem__(self, int key, float value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError

    def __repr__(self):
        return ', '.join((str(self.x), str(self.y)))

    def __sub__(self, cvec2 vec):
        return cvec2(self.x - vec.x, self.y - vec.y)

    def __add__(self, cvec2 vec):
        return cvec2(self.x + vec.x, self.y + vec.y)

    def __mul__(self, num):
        if isinstance(num, float) or isinstance(num, int):
            return cvec2(self.x * num, self.y * num)
        elif isinstance(num, cvec2):
            return cvec2(self.x * num.x, self.y * num.y)

    def __div__(self, float num):
        return cvec2(self.x / num, self.y / num)

    def __richcmp__(self, cvec2 other, int op):
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

    def __pow__(self, num, mod):
        return cvec2(self.x * self.x, self.y * self.y)

    def mag(self):
        """magnitude of the vector"""
        return sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        cdef float mag = self.mag()
        return cvec2(self.x / mag, self.y / mag)
