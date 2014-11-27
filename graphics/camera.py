from pyglet.gl import *
from menu.menu_events import Events
from player.cvec2 import cvec2 as vec2
from player import player

phext = player.phext
ext = vec2(*phext)


class Camera(Events):
    """docstring for Camera"""
    def __init__(self, window):
        super(Camera, self).__init__()
        width = window.width
        height = window.height
        self.window = window
        self.campos = vec2(- 2 * width, height / 2)
        self.target = vec2(self.campos.x, self.campos.y)
        self.wcoords = vec2(width / 2, height / 2)
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

    def __enter__(self):
        self.set_camera()

    def __exit__(self, type, value, tb):
        self.set_static()

    def update(self, dt, state):
        self.pos, self.vel = state.pos + ext, state.vel
        self.pos = vec2(*self.pos) * self.scale
        # velocity easing
        #if self.vel.x != 0:
        #self.eas_vel.x -= (self.eas_vel.x - self.vel.x) * dt
        #self.eas_vel.y -= (0*self.eas_vel.y + self.vel.y) * dt
        self.target = self.mpos - self.wcoords + self.pos
        self.campos -= (self.campos - self.target) * self.mul_easing * dt
        self.aimpos = self.campos + self.mpos - self.wcoords
        self.aimpos = vec2(self.aimpos.x / self.scale.x,
                           self.aimpos.y / self.scale.y)
        self.send_message('mousepos', self.aimpos)

    def set_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(10, 16./9, 0.1, 10000)
        x = self.campos.x
        y = self.campos.y
        gluLookAt(x, y, 3300 * self.scale.x, x, y, 0, 0, 1, 0)
        #glMatrixMode(GL_MODELVIEW)
        #glTranslatef(-self.campos.x + 2 * self.wcoords.x,
         #            -self.campos.y + self.wcoords.y, 2)

    def set_static(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glOrtho(0, self.window.width, 0, self.window.height, -1000, 1000)


    def receive_m_pos(self, event, msg):
        self.mpos.x, self.mpos.y = msg[0], msg[1]

    def mpos_from_aim(self, aimpos):
        mpos = vec2(aimpos.x * self.scale.x,
                    aimpos.y * self.scale.y) - self.campos + (self.wcoords
                                                             + self.offset) * 2
        self.mpos = vec2(*mpos)

    def interpolate_mpos(self):
        self.mpos_temp -= (self.mpos_temp - self.mpos) * 0.2
        return self.mpos_temp

    def on_resize(self, width, height):
        self.h = height / 2
        self.width = width / 2
