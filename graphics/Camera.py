from pyglet.gl import *


class Camera(object):
    """docstring for Camera"""
    def __init__(self, window):
        super(Camera, self).__init__()
        self.x = window.width / 2
        self.y = window.height / 2
        self.h = window.height / 2
        self.w = window.width / 2

    def get_mouse_pos(self, xy_arr):
        self.x = xy_arr[0]
        self.y = xy_arr[1]

    def set_camera(self):
        # gl.glViewport(- self.m_x + self.w, - self.m_y + self.h,
        #               self.w * 2, self.h * 2)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef(-self.x + self.w, -self.y + self.h, 0)

    def set_static(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
