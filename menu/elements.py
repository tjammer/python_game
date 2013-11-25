import pyglet
from graphics.primitives import Box


class TextBoxFramed(object):
    """docstring for Textbox_framed"""
    def __init__(self, pos, text, size=[300, 100], f_size=2):
        super(TextBoxFramed, self).__init__()
        self.pos = pos
        self.size = size
        self.f_size = f_size
        # code for text here
        self.Label = pyglet.text.Label(text, font_name='Helvetica',
                                       font_size=36, bold=False,
                                       x=self.pos[0] + self.size[0] / 2,
                                       y=self.pos[1] + self.size[1] / 2,
                                       anchor_x='center', anchor_y='center')
        self.Box = Box(pos, size, f_size)

    def in_box(self, m_pos):
        m_x = m_pos[0]
        m_y = m_pos[1]
        if m_x > self.pos[0] and m_x < self.pos[0] + self.size[0]:
            if m_y > self.pos[1] and m_y < self.pos[1] + self.size[1]:
                return True
        return False

    def draw(self):
        self.Box.draw()
        self.Label.draw()
