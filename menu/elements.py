import pyglet
from graphics.primitives import Box


class TextBoxFramed(object):
    """docstring for Textbox_framed"""
    def __init__(self, pos, text, size=[300, 100], f_size=2):
        super(TextBoxFramed, self).__init__()
        self.target_pos = pos
        self.pos = [0, pos[1]]
        self.size = size
        self.f_size = f_size
        # code for text here
        self.Label = pyglet.text.Label(text, font_name='Helvetica',
                                       font_size=36, bold=False,
                                       x=self.pos[0] + self.size[0] / 2,
                                       y=self.pos[1] + self.size[1] / 2,
                                       anchor_x='center', anchor_y='center')
        self.Box = Box(self.pos, size, f_size)

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

    def update(self):
        self.Box.update()
        self.Label.x = self.pos[0] + self.size[0] / 2
        self.Label.y = self.pos[1] + self.size[1] / 2


class Rectangle(object):
    '''Draws a rectangle into a batch.'''
    def __init__(self, x1, y1, x2, y2, batch):
        self.vertex_list = batch.add(4, pyglet.gl.GL_QUADS, None,
            ('v2i', [x1, y1, x2, y1, x2, y2, x1, y2]),
            ('c4B', [200, 200, 220, 255] * 4)
        )


class TextWidget(object):
    def __init__(self, text, x, y, width, batch):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=(0, 0, 0, 255))
                                )
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        pad = 2
        self.rectangle = Rectangle(x - pad, y - pad,
                                   x + width + pad, y + height + pad, batch)

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)
