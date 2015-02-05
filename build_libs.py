from distutils.core import setup
from Cython.Build import cythonize
from os import path

"""usage: python build_libs.py build_ext --inplace"""

# cvec2
setup(
    name="cvec2",
    ext_modules=cythonize(path.join('player', 'cvec2.pyx')))

# caabb
setup(
    name="caabb",
    ext_modules=cythonize(path.join('collision', 'caabb.pyx')))

# vec3
setup(
    name="vec3",
    ext_modules=cythonize(path.join('graphics', 'vec3.pyx')))

# animation
setup(
    name="animationquat",
    ext_modules=cythonize(path.join('graphics', 'animationquat.pyx')))
