from pyglet.gl import *


class Camera(object):
    """docstring for Camera"""
    def __init__(self, window):
        super(Camera, self).__init__()
        self.x = - 2 * window.width
        self.y = window.height / 2
        self.target_x = self.x
        self.target_y = self.y
        self.h = window.height / 2
        self.w = window.width / 2
        self.p_pos = 0
        self.mul_easing = .3
        self.m_x = 1280 / 2
        self.m_y = 720 / 2
        # y offset to have player in the lower half of the screen
        self.y_offset = -120
        self.eas_vel = 0

    def update(self, dt):
        # velocity easing
        if self.p_vel != 0:
            self.eas_vel -= (self.eas_vel - self.p_vel) * dt * 4.5
        self.target_x = self.m_x + self.p_pos + self.eas_vel * 0.5
        self.x -= (self.x - self.target_x) * self.mul_easing * dt * 30
        self.target_y = self.m_y + self.y_offset
        self.y -= (self.y - self.target_y) * self.mul_easing * dt * 30

    def set_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-self.x + 2 * self.w,
                     -self.y + self.h, 0)

    def set_static(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def receive_player_pos(self, event, msg):
        self.p_pos = msg[0]
        self.p_vel = msg[1]

    def receive_m_pos(self, event, msg):
        self.m_x = msg[0]
        self.m_y = msg[1]
