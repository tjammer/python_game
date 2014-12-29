from pyglet.gl import *
from menu.menu_events import Events
from player.cvec2 import cvec2 as vec2
from player import player
from matrix import Matrix
from shader import Shader

pext = player.phext


class Camera(Events):
    """docstring for Camera"""
    def __init__(self, window):
        super(Camera, self).__init__()
        width = window.width
        height = window.height
        self.window = window
        self.campos = vec2(- 2 * width, height / 2)
        self.target = vec2(self.campos.x, self.campos.y)
        self.wcoords = vec2(width / 2., height / 2.)
        self.pos = vec2(0, 0)
        self.vel = vec2(0, 0)
        self.mul_easing = .3 * 30
        self.mpos = vec2(self.wcoords.x, self.wcoords.y)
        # y offset to have player in the lower half of the screen
        self.offset = vec2(0, +self.wcoords.y / 2)
        self.eas_vel = vec2(0, 0)
        self.aimpos = vec2(0, 0)
        self.scale = vec2(window.width / 1360., window.height / 765.)
        self.mpos_temp = vec2(0, 0)
        #shader
        self.shader = Shader('camera')
        self.zoom = 34
        self.t = 0

    def __enter__(self):
        return self.set_camera()

    def __exit__(self, type, value, tb):
        self.set_static()

    def update(self, dt, state):
        self.pos, self.vel = state.pos + pext, state.vel
        self.pos = vec2(*self.pos) * self.scale
        self.set_zoom(dt)
        self.target = (self.mpos - self.wcoords)*.63 + self.pos
        self.campos -= (self.campos - self.target) * self.mul_easing * dt
        self.aimpos = self.campos + self.mpos - self.wcoords
        self.aimpos = vec2(self.aimpos.x / self.scale.x,
                           self.aimpos.y / self.scale.y)
        self.send_message('mousepos', self.aimpos)

    def set_camera(self):
        mvp = Matrix.perspective(16, 9, self.zoom, .8, 2000)
        x = self.campos.x
        y = self.campos.y
        mvp = mvp.look_at(x, y, 800 * self.scale.x, x, y, 0, 0, 1, 0)
        self.shader.set('mvp', mvp)
        self.shader.push()
        return mvp

    def set_static(self):
        self.shader.pop()

    def ease(self, t, b, c, d):
        t /= d
        if (t < 1):
            return c/2*t*t + b
        t -= 1
        return -c/2 * (t*(t-2) - 1) + b

    def set_zoom(self, dt):
        self.t -= (self.t - abs(self.vel.x))*dt
        self.zoom = self.ease(self.t, 30, 24, 500)

    def receive_m_pos(self, event, msg):
        self.mpos.x, self.mpos.y = msg[0], msg[1]

    def mpos_from_aim(self, aimpos):
        mpos = vec2(aimpos.x * self.scale.x,
                    aimpos.y * self.scale.y) - self.campos + (
            self.wcoords + self.offset) * 2
        self.mpos = vec2(*mpos)

    def interpolate_mpos(self):
        self.mpos_temp -= (self.mpos_temp - self.mpos) * 0.2
        return self.mpos_temp

    def on_resize(self, width, height):
        self.h = height / 2
        self.width = width / 2
