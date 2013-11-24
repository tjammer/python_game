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
        self.m_x = 0
        self.m_y = 0

    def update(self, dt):
        # self.x = xy_arr[0]
        # self.y = xy_arr[1]
        self.target_x = self.m_x + self.p_pos + self.p_vel
        self.x -= (self.x - self.target_x) * self.mul_easing * dt * 30
        self.target_y = self.m_y
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

    def receive_mouse_pos(self, event, msg):
        self.m_x = msg[0]
        self.m_y = msg[1]
