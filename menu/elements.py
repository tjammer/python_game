import pyglet
from graphics.primitives import Box, Rect


class TextBoxFramed(object):
    """docstring for Textbox_framed"""
    def __init__(self, pos, text, size=[300, 100], f_size=2, batch=None):
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
                                       anchor_x='center', anchor_y='center',
                                       batch=batch)
        self.Box = Box(self.pos, size, f_size, batch=batch)

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

    def restore(self):
        self.Box.restore()

    def highlight(self):
        self.Box.highlight()


class ColCheckBox(object):
    """docstring for ColCheckBox"""
    def __init__(self, pos, batch, color, size=(40, 40), hcolor=(255, 255, 0),
                 activecolor=(255, 255, 255), inactivecolor=(25, 25, 25)):
        super(ColCheckBox, self).__init__()
        self.pos = pos
        self.target_pos = pos
        self.size = size
        self.color = color
        self.hcolor = hcolor
        self.activecolor = activecolor
        self.inactivecolor = inactivecolor
        self.box = Box(pos, size, color=inactivecolor, hcolor=hcolor,
                       batch=batch, innercol=color)
        self.ccolor = self.inactivecolor

    def highlight(self):
        self.box.outer_box.ver_list.colors = list(self.hcolor) * 4

    def restore(self):
        self.box.outer_box.ver_list.colors = list(self.ccolor) * 4

    def activate(self):
        self.ccolor = self.activecolor

    def deactivate(self):
        self.ccolor = self.inactivecolor

    def draw(self):
        self.box.draw()

    def update(self):
        pass

    def in_box(self, mpos):
        m_x = mpos[0]
        m_y = mpos[1]
        if m_x > self.pos[0] and m_x < self.pos[0] + self.size[0]:
            if m_y > self.pos[1] and m_y < self.pos[1] + self.size[1]:
                return True
        return False


class TextWidget(object):
    def __init__(self, text, x, y, width, batch, window, **kwargs):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=(255, 255, 255, 255), **kwargs)
                                )
        font = self.document.get_font()
        height = font.ascent - font.descent

        self.layout = pyglet.text.layout.IncrementalTextLayout(
            self.document, width, height, multiline=False, batch=batch)
        self.caret = pyglet.text.caret.Caret(self.layout)
        self.caret.color = [255] * 3

        self.layout.x = x
        self.layout.y = y

        # Rectangular outline
        self.rectangle = Rect(x, y, width, height, batch=batch,
                              color=(25, 25, 25))

        self.window = window
        self.text_cursor = window.get_system_mouse_cursor('text')
        self.focus = None
        self.set_focus(self)

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            if self.hit_test(x, y):
                self.window.set_mouse_cursor(self.text_cursor)
            else:
                self.window.set_mouse_cursor(None)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            if self.hit_test(x, y):
                self.set_focus(self)
            else:
                self.set_focus(None)

            if self.focus:
                self.focus.caret.on_mouse_press(x, y, button, modifiers)

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            if self.focus:
                self.focus.caret.on_mouse_drag(x, y, dx, dy, buttons,
                                               modifiers)

        @self.window.event
        def on_text(text):
            if self.focus:
                self.focus.caret.on_text(text)

        @self.window.event
        def on_text_motion(motion):
            if self.focus:
                self.focus.caret.on_text_motion(motion)

        @self.window.event
        def on_text_motion_select(motion):
            if self.focus:
                self.focus.caret.on_text_motion_select(motion)

    def hit_test(self, x, y):
        return (0 < x - self.layout.x < self.layout.width and
                0 < y - self.layout.y < self.layout.height)

    def set_focus(self, focus):
        if self.focus:
            self.focus.caret.visible = False
            self.focus.caret.mark = self.focus.caret.position = 0

        self.focus = focus
        if self.focus:
            self.focus.caret.visible = True
            self.focus.caret.mark = 0
            self.focus.caret.position = len(self.focus.document.text)
