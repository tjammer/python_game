#=== SHADER =================================================================
# Fragment shaders, filters, Frame Buffer Object (FBO)
# Authors: Tom De Smedt, Frederik De Bleser
# License: BSD (see LICENSE.txt for details).
# Copyright (c) 2008 City In A Bottle (cityinabottle.org)
# http://cityinabottle.org/nodebox
# modified by Tobias Jammer in 2014

from pyglet.gl import *
from pyglet.image import Texture
from matrix import Matrix
from os import path
from ctypes import *
from extensions.glext_arb import *


def next(generator, default=None):
    try:
        return generator.next()
    except StopIteration:
        return default


class vector(tuple):
    pass


def vec2(f1, f2):
    return vector((f1, f2))


def vec3(f1, f2, f3):
    return vector((f1, f2, f3))


def vec4(f1, f2, f3, f4):
    return vector((f1, f2, f3, f4))

COMPILE = "compile"  # Error occurs during glCompileShader().
BUILD = "build"  # Error occurs during glLinkProgram().


class ShaderError(Exception):
    def __init__(self, value, type=COMPILE):
        Exception.__init__(self, "%s error: %s" % (type, value))
        self.value = value
        self.type = type


class Shader(object):

    def __init__(self, name):
        with open(path.join('graphics', 'shaders', name + '.vs'), 'r') as f:
            vertex = f.read()
        with open(path.join('graphics', 'shaders', name + '.fs'), 'r') as f:
            fragment = f.read()
        self._vertex = vertex   # GLSL source for vertex shader.
        self._fragment = fragment  # GLSL source for fragment shader.
        self._compiled = []
        self._program = None
        self._active = False
        self.variables = {}
        self._build()

    def __enter__(self):
        self.push()

    def __exit__(self, type, value, tb):
        self.pop()

    def _compile(self, source, type=GL_VERTEX_SHADER):
        # Compile the GLSL source code, either as GL_FRAGMENT_SHADER or GL_VERTEX_SHADER.
        # If the source fails to compile, retrieve the error message and raise ShaderError.
        # Store the compiled shader so we can delete it later on.
        shader = glCreateShader(type)
        status = c_int(-1)
        glShaderSource(shader, 1, cast(pointer(c_char_p(source)),
                       POINTER(POINTER(c_char))), None)
        glCompileShader(shader)
        glGetShaderiv(shader, GL_COMPILE_STATUS, byref(status))
        if status.value == 0:
            raise self._error(shader, type=COMPILE)
        self._compiled.append(shader)
        return shader

    def _build(self):
        # Each Shader has its own OpenGL rendering program and you need to switch between them.
        # Compile fragment and vertex shaders and build the program.
        program = glCreateProgram()
        status = c_int(-1)
        if self._vertex:
            glAttachShader(program, self._compile(self._vertex,
                           GL_VERTEX_SHADER))
        if self._fragment:
            glAttachShader(program, self._compile(self._fragment,
                           GL_FRAGMENT_SHADER))
        glLinkProgram(program)
        glGetProgramiv(program, GL_LINK_STATUS, byref(status))
        if status.value == 0:
            raise self._error(program, type=BUILD)
        self._program = program

    def _error(self, obj, type=COMPILE):
        # Get the info for the failed glCompileShader() or glLinkProgram(),
        # delete the failed shader or program,
        # return a ShaderError with the error message.
        f1 = type == COMPILE and glGetShaderiv or glGetProgramiv
        f2 = type == COMPILE and glGetShaderInfoLog or glGetProgramInfoLog
        f3 = type == COMPILE and glDeleteShader or glDeleteProgram
        length = c_int()
        f1(obj, GL_INFO_LOG_LENGTH, byref(length))
        msg = ""
        if length.value > 0:
            msg = create_string_buffer(length.value)
            f2(obj, length, byref(length), msg)
            msg = msg.value
        f3(obj)
        return ShaderError(msg, type)

    def get(self, name):
        """ Returns the value of the variable with the given name.
        """
        return self.variables[name]

    def set(self, name, value):
        """ Set the value of the variable with the given name in the GLSL source script.
            Supported variable types are: vec2(), vec3(), vec4(), single int/float, list of int/float.
            Variables will be initialized when Shader.push() is called (i.e. glUseProgram).
        """
        self.variables[name] = value
        if self._active:
            self._set(name, value)

    def __setattr_(self, name, value):
        self.name = value
        if self._active:
            self._set(name, value)

    def _set(self, name, value):
        address = glGetUniformLocation(self._program, name)
        # A vector with 2, 3 or 4 floats representing vec2, vec3 or vec4.
        if isinstance(value, vector):
            if len(value) == 2:
                glUniform2f(address, value[0], value[1])
            elif len(value) == 3:
                glUniform3f(address, value[0], value[1], value[2])
            elif len(value) == 4:
                glUniform4f(address, value[0], value[1], value[2], value[3])
        # A list representing an array of ints or floats.
        elif isinstance(value, (list, tuple)):
            if next((v for v in value if isinstance(v, vector))) is not None:
                data = ((GLfloat * 4)*33)(*value)
                glUniform4fv(address, 33, cast(data, POINTER(GLfloat)))
            elif next((v for v in value if isinstance(v, float))) is not None:
                array = c_float * len(value)
                glUniform1fv(address, len(value), array(*value))
            else:
                array = c_int * len(value)
                glUniform1iv(address, len(value), array(*value))
        # Single float value.
        elif isinstance(value, float):
            glUniform1f(address, value)
        # Single int value or named texture.
        elif isinstance(value, int):
            glUniform1i(address, value)
        elif isinstance(value, Matrix):
            #value.do_set(address)
            glUniformMatrix4fv(address, 1, GL_TRUE, value.values)
        else:
            ShaderError, "don't know how to handle variable %s" % value.__class__

    def push(self):
        """ Installs the program and sets its variables.
            When you use the image() command between shader.push() and shader.pop(),
            the shader's effect will be applied to the image before drawing it.
            To use shader effects in combination with paths,
            draw the path in an offscreen buffer, render it, and apply to effect to the render.
        """
        self._active = True
        glUseProgram(self._program)
        for k, v in self.variables.items():
            self._set(k, v)

    def pop(self):
        # Note that shaders can't be nested since they all have their own program,
        # pop() just removes any active program.
        if self._active == True:
            glUseProgram(0)
            self._active = False

    @property
    def active(self):
        return self._active

    @property
    def source(self):
        return (self._vertex, self._fragment)

    def __del__(self):
        try:
            for shader in self._compiled:
                if glDetachShader and self._program:
                    glDetachShader(self._program, shader)
                if glDeleteShader:
                    glDeleteShader(shader)
            if glDeleteProgram:
                glDeleteProgram(self._program)
        except:
            pass


#=====================================================================================================

#--- FRAME BUFFER OBJECT -----------------------------------------------------------------------------
# Based on "Frame Buffer Object 101" (2006), Rob Jones,
# http://www.gamedev.net/reference/articles/article2331.asp

_UID = 0


def _uid():
    # Each FBO has a unique ID.
    global _UID; _UID += 1; return _UID;


def _texture(width, height):
    # Returns an empty texture of the given width and height.
    return Texture.create(width, height)


attachements = (GL_COLOR_ATTACHMENT0,
                GL_COLOR_ATTACHMENT1,
                GL_COLOR_ATTACHMENT2)
deferred_texs = ('diffuse', 'verts', 'norms')


class OffscreenBufferError(Exception):
    pass


class OffscreenBuffer(object):

    def __init__(self, width, height, mult=3):
        self.id = c_uint(_uid())
        try:
            glGenFramebuffers(1, byref(self.id))
        except:
            raise (OffscreenBufferError, "offscreen buffer not supported.")
        assert mult <= len(attachements)
        self.mult = mult
        self.textures = []
        self.buffers = None
         # The canvas bounds, set in OffscreenBuffer.push().
        self._viewport = (None, None, None, None)
        self._active = False
        self._init(width, height)
        self._init_depthbuffer(width, height)

    def __enter__(self):
        self.clear()
        self.push()

    def __exit__(self, type, value, tb):
        self.pop()

    def __iter__(self):
        return iter(self.textures)

    def _init(self, width, height):
        glBindFramebuffer(GL_FRAMEBUFFER, self.id.value)
        for i in range(self.mult):
            self.textures.append(_texture(int(width), int(height)))
            glBindTexture(self.textures[i].target, self.textures[i].id)
            glFramebufferTexture2D(
                GL_FRAMEBUFFER, attachements[i], self.textures[i].target,
                self.textures[i].id, self.textures[i].level)
        buffers = GLenum * self.mult
        self.buffers = buffers(GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1,
                               GL_COLOR_ATTACHMENT2)

    @property
    def width(self):
        return self.texture.width

    @property
    def height(self):
        return self.texture.height

    @property
    def active(self):
        return self._active

    def push(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.id.value)
        glDrawBuffers(self.mult, self.buffers)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise OffscreenBufferError
        glEnable(GL_DEPTH_TEST)
        self._active = True

    def pop(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glBlendFuncSeparate(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, GL_ONE,
                            GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)
        self._active = False

    def draw(self):
        self.textures[0].blit(0, 0)

    def slice(self, x, y, width, height):
        """ Returns a portion of the offscreen buffer as an image.
        """
        return self.texture.get_region(x, y, width, height)

    def reset(self, width=None, height=None):
        """ Resizes the offscreen buffer by attaching a new texture to it.
            This will destroy the contents of the previous buffer.
            If you do not explicitly reset the buffer, the contents from previous drawing
            between OffscreenBuffer.push() and OffscreenBuffer.pop() is retained.
        """
        if self._active:
            raise (OffscreenBufferError,
                   "can't reset offscreen buffer when active")
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        self._init(width, height)

    def clear(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glClear(GL_DEPTH_BUFFER_BIT)
        glClear(GL_STENCIL_BUFFER_BIT)

    def _init_depthbuffer(self, width, height):
        self._depthbuffer = c_uint(_uid())
        glGenRenderbuffers(1, byref(self._depthbuffer))
        glBindRenderbuffer(GL_RENDERBUFFER, self._depthbuffer)
        glRenderbufferStorage(
            GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, int(width), int(height))
        glFramebufferRenderbuffer(
            GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT,
            GL_RENDERBUFFER, self._depthbuffer)

    def __del__(self):
        try:
            if glDeleteFramebuffers:
                glDeleteFramebuffers(1, self.id)
            if glDeleteRenderbuffers and hasattr(self, "_depthbuffer"):
                glDeleteRenderbuffers(1, self._depthbuffer)
        except:
            pass
