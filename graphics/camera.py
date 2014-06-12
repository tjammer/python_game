from pyglet.gl import *
from menu.menu_events import Events
from player.state import vec2


class Camera(Events):
    """docstring for Camera"""
    def __init__(self, window):
        super(Camera, self).__init__()
        self.campos = vec2(- 2 * window.width, window.height / 2)
        self.target = vec2(self.campos.x, self.campos.y)
        self.wcoords = vec2(window.width / 2, window.height / 2)
        self.pos = vec2(0, 0)
        self.vel = vec2(0, 0)
        self.mul_easing = .3 * 30
        self.mpos = vec2(self.wcoords.x, self.wcoords.y)
        # y offset to have player in the lower half of the screen
        self.offset = vec2(0, -self.wcoords.y / 2)
        self.eas_vel = vec2(0, 0)
        self.aimpos = vec2(0, 0)

    def update(self, dt, state):
        self.pos, self.vel = state.pos, state.vel
        # velocity easing
        if self.vel.x != 0:
            self.eas_vel.x -= (self.eas_vel.x - self.vel.x) * dt * 4.5
        #self.eas_vel.y -= (0*self.eas_vel.y + self.vel.y) * dt
        self.target = self.mpos + self.pos + self.eas_vel * 0.5 + self.offset
        self.campos -= (self.campos - self.target) * self.mul_easing * dt
        #print self.x + self.m_x - 2 * self.w
        self.aimpos = self.campos + self.mpos - (self.wcoords+self.offset) * 2
        self.send_message('mousepos', self.aimpos)

    def set_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-self.campos.x + 2 * self.wcoords.x,
                     -self.campos.y + self.wcoords.y, 0)

    def set_static(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def receive_m_pos(self, event, msg):
        self.mpos.x, self.mpos.y = msg[0], msg[1]

    def on_resize(self, width, height):
        self.h = height / 2
        self.width = width / 2
