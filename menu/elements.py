import pyglet
from graphics.primitives import Box, Rect, font
from network_utils import protocol_pb2 as proto
from pyglet.text.document import FormattedDocument as Doc
from pyglet.text.layout import ScrollableTextLayout as Layout
from player.state import vec2
from pyglet.text import Label
from itertools import chain

inpt = proto.Input()
inputdict = {'left': 'left', 'right': 'right', 'up': 'jump', 'att': 'attack',
             'rdy': 'ready up', 'chat': 'chat'}
weaponsdict = {'melee': 'melee', 'sg': 'shotgun',
               'lg': 'lightning gun', 'blaster': 'blaster',
               'gl': 'grenades'}

unity = vec2(1, 1)


class TextBoxFramed(object):
    """docstring for Textbox_framed"""
    def __init__(self, pos, text, size=[300, 100], f_size=2, batch=None,
                 font_size=36, animate=True, **kwargs):
        super(TextBoxFramed, self).__init__()
        self.target_pos = pos
        if animate:
            self.pos = [0, pos[1]]
        else:
            self.pos = pos
        self.animate = animate
        self.width = size[0]
        self.height = size[1]
        self.f_size = f_size
        # code for text here
        self.Label = pyglet.text.Label(text, font_name=font,
                                       font_size=font_size, bold=False,
                                       x=self.pos[0] + self.width / 2,
                                       y=self.pos[1] + self.height / 2,
                                       anchor_x='center', anchor_y='center',
                                       batch=batch)
        self.Box = Box(self.pos, [self.width, self.height], f_size,
                       batch=batch, **kwargs)

    def in_box(self, m_pos):
        m_x = m_pos[0]
        m_y = m_pos[1]
        if m_x > self.pos[0] and m_x < self.pos[0] + self.width:
            if m_y > self.pos[1] and m_y < self.pos[1] + self.height:
                return True
        return False

    def draw(self):
        self.Box.draw()
        self.Label.draw()

    def update(self):
        self.Box.update()
        if self.animate:
            self.Label.x = self.pos[0] + self.width / 2
            self.Label.y = self.pos[1] + self.height / 2

    def scale_box(self):
        self.Box.new_size(self.width, self.height)

    def restore(self):
        self.Box.restore()

    def highlight(self):
        self.Box.highlight()


class ColCheckBox(object):
    """docstring for ColCheckBox"""
    def __init__(self, pos, batch, color, size=(40, 40), hcolor=(255, 255, 0),
                 activecolor=(255, 255, 255), inactivecolor=(25, 25, 25)):
        super(ColCheckBox, self).__init__()
        self.pos = vec2(*pos)
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

    def over_button(self, x, y):
        return (0 < x - self.pos.x < self.size[0] and
                0 < y - self.pos.y < self.size[1])


class TextWidget(object):
    def __init__(self, text, x, y, width, batch, window, **kwargs):
        self.document = pyglet.text.document.UnformattedDocument(text)
        self.document.set_style(0, len(self.document.text),
                                dict(color=(255, 255, 255, 255), **kwargs))
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


class KeysFrame(object):
    """docstring for KeysFrame"""
    def __init__(self, pos, width, height, window, batch,
                 line_space=None, font_size=24, hcolor=(25, 25, 25),
                 scl=unity):
        super(KeysFrame, self).__init__()
        self.scale = scl
        self.pos = vec2(*pos) * scl
        self.target_pos = pos
        self.window = window
        self.line_space = (line_space + font_size) * self.scale.x
        self.font_size = font_size * self.scale.x
        self.width = width * self.scale.x
        self.height = height * self.scale.y
        self.hcolor = hcolor

        self.doc = Doc('\n')
        self.layout = Layout(self.doc, width=self.width, height=self.height,
                             multiline=True, batch=batch)
        self.doc.set_paragraph_style(0, 0, dict(indent=None,
                                     line_spacing=self.line_space,
                                     font_size=self.font_size))

        self.layout.anchor_x = 'left'
        self.layout.anchor_y = 'top'
        self.layout.x = self.pos[0]
        self.layout.y = self.pos[1]

        self.even = 0
        self.active_i = []
        self.curr_line = None
        self.active_line = None

        @self.window.event
        def on_mouse_scroll(x, y, scroll_x, scroll_y):
            self.layout.view_y = scroll_y * self.layout.content_height
        self.handler = on_mouse_scroll

    def remove_handler(self):
        self.window.remove_handler('on_mouse_scroll', self.handler)

    def insert(self, action, key):
        self.even += 1
        iseven = self.even % 2
        action = dict(weaponsdict.items() + inputdict.items())[action]
        text = action + '\t' + key
        #i have no clue how to calculate the width properly
        length = pyglet.text.Label(key, font_size=self.font_size)
        length = length.content_width
        stop = self.width - length
        text += ' ' * 6
        self.doc.insert_text(len(self.doc.text),
                             text + '\n',
                             dict(font_size=self.font_size, color=[255] * 4,
                                  background_color=[50 * iseven] * 3 + [255]))
        ln = len(self.doc.text) - 3
        self.doc.set_paragraph_style(ln, ln,
                                     dict(tab_stops=[stop],
                                          indent=None,
                                          line_spacing=self.line_space,
                                          wrap=False))

    def in_box(self, mpos):
        x, y = mpos
        self.mpos = mpos
        return (0 < x - self.layout.x < self.layout.width and
                0 < self.layout.y - y < self.layout.height)

    def over_button(self, x, y):
        self.mpos = (x, y)
        return (0 < x - self.layout.x < self.layout.width and
                0 < self.layout.y - y < self.layout.height)

    def highlight(self):
        y = self.layout.y - self.mpos[1] - self.layout.view_y
        lines = self.doc.text.split('\n')
        num = int(float(y) / self.line_space + 0.45)
        try:
            if not self.active_line:
                action, key = lines[num].split('\t')
                ind = self.doc.text.find(action) + 1
                if (ind, num) not in self.active_i:
                    self.curr_line = (ind, num)
                    self.restore()
                    self.doc.set_paragraph_style(ind, ind, dict(
                                                 background_color=
                                                 self.hcolor + (255,)))
                    self.active_i.append((ind, num))
        except (IndexError, ValueError):
            self.restore()

    def restore(self):
        if len(self.active_i) > 0:
            for a in self.active_i:
                ind, num = a
                if not a == self.active_line:
                    self.doc.set_paragraph_style(ind, ind, dict(
                                                 background_color=
                                                 [50 * (num % 2)] * 3 + [255]))
            self.active_i = []
            if (ind, num) == self.curr_line:
                self.curr_line = None

    def activate(self):
        if not self.curr_line:
            return
        self.active_line = self.curr_line
        ind, num = self.active_line
        self.doc.set_paragraph_style(ind, ind, dict(background_color=
                                                    (255, 128, 0) + (255,)))

    def deactivate(self):
        self.active_line = None
        self.restore()

    def get_action(self):
        ind, num = self.active_line
        action, key = self.doc.text.split('\n')[num].split('\t')
        self.layout.delete()
        return action

    def update(self):
        pass

hcolor = (255, 128, 0)
topcolor = (0, 128, 255)
botcolor = (25,)*3
toplinecolor = (255,)*3
botlinecolor = (255, 128, 0)


class Button(object):
    """docstring for Button"""
    def __init__(self, text, x, y, width, height, batch, color=(50, 50, 50),
                 scale=unity, **kwargs):
        super(Button, self).__init__()
        self.pos = vec2(x, y) * scale
        self.width = width * scale.x
        self.height = height * scale.y
        self.bsize = 2 * scale.x
        self.color = color
        self.hcolor = hcolor
        self.text = Label(text, x=(self.pos.x + self.width / 2),
                          y=(self.pos.y + self.height / 2),
                          anchor_x='center', anchor_y='center',
                          batch=batch, **kwargs)
        self.bound = Rect(self.pos.x - self.bsize, self.pos.y - self.bsize,
                          self.width+2*self.bsize, self.height+2*self.bsize,
                          color=toplinecolor, batch=batch)
        self.rect = Rect(self.pos.x, self.pos.y, self.width, self.height,
                         color=self.color, batch=batch)

    def highlight(self):
        self.rect.update_color(self.hcolor)

    def restore(self):
        if not self.rect.color == self.color:
            self.rect.update_color(self.color)

    def over_button(self, x, y):
        return (0 < x - self.pos.x < self.width and
                0 < y - self.pos.y < self.height)

    def delete(self):
        self.text.delete()
        self.rect.delete()


class LineButton(object):
    def __init__(self, text, x, y, width, height, lheight, batch,
                 color=(50, 50, 50), scale=unity, **kwargs):
        super(LineButton, self).__init__()
        self.pos = vec2(x, y) * scale
        self.width = width * scale.x
        self.height = height * scale.y
        self.bsize = 1 * scale.x
        self.color = color
        self.hcolor = hcolor
        self.text = Label(text, x=(self.pos.x + self.width / 2),
                          y=(self.pos.y + self.height / 2),
                          anchor_x='center', anchor_y='top',
                          batch=batch, **kwargs)
        self.rect = Rect(self.pos.x, self.pos.y, self.width, lheight*scale.y,
                         color=self.color, batch=batch)

    def highlight(self):
        self.rect.update_color(self.hcolor)

    def restore(self):
        if not self.rect.color == self.color:
            self.rect.update_color(self.color)

    def over_button(self, x, y):
        return (0 < x - self.pos.x < self.width and
                0 < y - self.pos.y < self.height)


class MenuLayout(object):
    """docstring for MenuLayout"""
    def __init__(self, batch, scale):
        super(MenuLayout, self).__init__()
        self.headline = []
        self.center = 0
        self.bottom = []
        self.tabs = {}
        self.scale = scale
        self.batch = batch
        self.actives = {}
        self.button_fs = 16 * self.scale.x
        #bottom top line height
        self.btlh = 120
        #line height
        self.lheight = 3

    def __iter__(self):
        return self.actives.iteritems()

    def add_headline(self, text):
        #rects for background and line,respectively
        if len(self.headline) != 0:
            for item in self.headline:
                item.delete()
            self.headline = []
        self.headline.append(Rect(x=0, y=(720-self.btlh)*self.scale.y,
                             width=1280*self.scale.x,
                             height=self.btlh*self.scale.y,
                             color=topcolor, batch=self.batch))
        self.headline.append(Rect(x=0, width=1280*self.scale.x,
                             y=(720-self.btlh-self.lheight)*self.scale.y,
                             height=self.lheight*self.scale.y,
                             color=(255,)*3, batch=self.batch))
        self.headline.append(Label(text, x=640*self.scale.x,
                             y=(720-self.btlh/2)*self.scale.y, font_name=font,
                             font_size=24 * self.scale.x,
                             anchor_x='center', anchor_y='bottom',
                             batch=self.batch, color=(255,)*4))

    def add_bottom(self, lst):
        #background
        if len(lst) == 0:
            return
        if len(self.bottom) == 0:
            self.bottom.append(Rect(x=0, y=0*self.scale.y,
                               width=1280*self.scale.x,
                               height=self.btlh*self.scale.y,
                               color=botcolor, batch=self.batch))
            self.bottom.append(Rect(x=0, y=self.btlh*self.scale.y,
                               width=1280*self.scale.x,
                               height=self.lheight*self.scale.y,
                               color=botlinecolor, batch=self.batch))
            self.bottom.append(True)

        spacing = 1280 / (len(lst) + 1)

        width = max(len(i[1]) * 72. / 96 * self.button_fs for i in lst) + 40

        for i, text in enumerate(lst):
            key, text = text
            self.actives[key] = Button(text,
                                       ((i+1)*spacing - width / 2),
                                       (self.btlh - 80)/2, width,
                                       80, batch=self.batch, scale=self.scale,
                                       font_size=self.button_fs)

    def add_center(self, lst):

        spacing = (720 - 2*(self.btlh + self.lheight)) / (len(lst) + 1)
        width = max(len(i[1]) * 72. / 96 * self.button_fs for i in lst) + 40

        for i, text in enumerate(reversed(lst)):
            key, text = text
            self.actives[key] = Button(text, 640 - width / 2,
                                       self.btlh+self.lheight+(i+1)*spacing-40,
                                       width, 80, batch=self.batch,
                                       scale=self.scale,
                                       font_size=self.button_fs, bold=False)

    def add_tabs(self, lst):
        if len(lst) == 0:
            return
        #background
        if not self.headline:
            self.add_headline('')

        width = max(len(i[1]) * 72. / 96 * self.button_fs for i in lst) + 40

        for i, text in enumerate(lst):
            try:
                key, text = text
                color = toplinecolor
            except ValueError:
                key, text, spam = text
                color = botlinecolor

            x = 1.5 * width + 20
            y = 720-self.btlh-self.lheight
            self.actives[key] = LineButton(text, i*x, y, width, 80,
                                           batch=self.batch, scale=self.scale,
                                           font_size=self.button_fs,
                                           color=color, lheight=self.lheight)

    def item_gen(self):
        hlgen = iter(self.headline)
        btgen = iter(self.bottom)
        acgen = self.actives.itervalues()
        return chain(hlgen, btgen, acgen)
