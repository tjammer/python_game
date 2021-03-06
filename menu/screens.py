# file for all the screens in the game
from menu_events import NewMenu as MenuClass
from elements import TextBoxFramed as btn, TextWidget, ColCheckBox as ccb
from elements import PopMenu
from pyglet.text import Label
from graphics.primitives import Box, font
from pyglet.window import key
from elements import *
from player import options
from itertools import chain
from graphics import wmodes


class MainMenu(MenuClass):
    """docstring for MainMenu"""
    def __init__(self, window, *args, **kwargs):
        super(MainMenu, self).__init__(window=window, *args, **kwargs)
        #self.layout.add_center([('start', 'start game'), ('options',)*2])
        colors = {'fg': (0, 128, 255, 255), 'bg': (0, 0, 0, 0),
                  'fg_selec': (255, 128, 0, 255), 'other': (25, 25, 25, 255),
                  'font': (25, 25, 25, 255)}
        self.el_manager = ElementManager(window, colors, self.layout.actives,
                                         self.batch)
        self.el_manager.add(VerticalLine, pos=(0.11, 0), size=(0.01, 1),
                            anchor_y='b')
        self.el_manager.add(LButton, pos=(0.2, 0.76), size=(0.2, 0.1),
                            text='start game')
        self.el_manager.add(LButton, pos=(0.2, 0.53), size=(0.2, 0.1),
                            text='options')
        self.el_manager.add(LButton, pos=(0.2, 0.30), size=(0.2, 0.1),
                            text='quit game')

        self.layout.add_bottom([])
        self.layout.add_headline('gaem')

    def handle_clicks(self, key):
        if key == 'quit game':
            self.send_message('kill_self')
        if key == 'start game':
            self.send_message('start_game')
        if key == 'options':
            self.send_message('menu_transition_+',
                              (PlayerOptions, self.window))


class QuitScreen(MenuClass):
    """docstring for QuitScreen"""
    def __init__(self, *args, **kwargs):
        super(QuitScreen, self).__init__(*args, **kwargs)
        self.buttons['quit'] = btn([300, 300], 'yes', batch=self.batch)
        self.buttons['dont_quit'] = btn([680, 300], 'no', batch=self.batch)
        self.text = 'do you really want to quit?'
        self.Label = Label(self.text, font_name=font,
                           font_size=36, bold=False,
                           x=640, y=500, anchor_x='center',
                           anchor_y='center', batch=self.batch)
        self.Box = Box([340, 200], [600, 400], 2)
        self.do_scale()

    def handle_clicks(self, key):
        if key == 'quit':
            self.send_message('kill_self')
        if key == 'dont_quit':
            self.send_message('menu_transition_-')


class GameMenu(MenuClass):
    """docstring for GameMenu
    main menu ingame"""
    def __init__(self, *args, **kwargs):
        super(GameMenu, self).__init__(*args, **kwargs)
        #self.buttons['resume'] = btn([500, 400], 'resume game',
         #                            batch=self.batch)
        self.layout.add_headline('ingame menu')
        self.layout.add_center([('resume', 'resume game')])
        #self.buttons['to_main'] = btn([500, 200], 'main menu',
        #                              batch=self.batch)
        if self.bool:
            st = 'join game'
        else:
            st = 'spectate'
        self.layout.add_bottom([('to_main', 'main menu'), ('join_game', st)])
        self.cd = 0
       ### self.do_scale()

    def handle_clicks(self, key):
        if key == 'resume':
            self.send_message('menu_transition_-')

        if key == 'to_main':
            self.send_message('to_main')

        if key == 'join_game' and not self.cd:
            self.send_message('try_join')
            self.cd = 1

    def add_update(self, dt):
        if self.cd:
            self.cd -= dt
            if self.cd < 0:
                self.cd = 0

        if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
            self.send_message('menu_transition_-')


class LoadScreen(MenuClass):
    """docstring for LoadScreen"""
    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)
        self.label = Label('connecting to server', font_name=font,
                           font_size=36, bold=False, x=200, y=550,
                           anchor_x='left', anchor_y='baseline',
                           batch=self.batch)

    def on_connect(self):
        self.send_message('menu_transition_-')

    def add_update(self, dt):
        try:
            if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
                self.send_message('to_main')
        except:
            pass

    def draw(self):
        self.window.clear()
        self.batch.draw()


class ChatScreen(MenuClass):
    """docstring for ChatScreen"""
    def __init__(self, *args, **kwargs):
        super(ChatScreen, self).__init__(*args, **kwargs)
        #self.window = window
        self.widget = TextWidget('', 200, 100, self.window.width - 500,
                                 self.batch, self.window)

    """def on_draw(self):
        self.batch.draw()"""

    def add_update(self, dt):
        if (self.keys[key.ENTER]
                and not self.keys_old[key.ENTER]) and (
                self.widget.focus and len(self.widget.document.text) > 0):
            if len(self.widget.document.text.strip()) > 0:
                self.send_message('chat', self.widget.document.text.strip())
            self.send_message('menu_transition_-')

        if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
            self.send_message('menu_transition_-')


class PlayerOptions(MenuClass):
    """docstring for PlayerOptions"""
    def __init__(self, arg, *args, **kwargs):
        super(PlayerOptions, self).__init__(*args, **kwargs)
        try:
            self.window, self.options = arg
        except TypeError:
            self.window = arg
            self.options = options.Options()
        self.layout.add_headline('options')
        self.layout.add_bottom([('cancel',)*2, ('save',)*2])
        self.layout.add_tabs([('this', 'player', True), ('keys', 'controls'),
                             ('graphics',)*2])
        self.namelabel = Label('name', font_name=font,
                               font_size=24*self.scale.x, bold=False,
                               x=200*self.scale.x, y=500*self.scale.y,
                               anchor_x='left', anchor_y='center',
                               batch=self.batch)
        self.widget = TextWidget(self.options['name'], 500*self.scale.x,
                                 (500)*self.scale.y - 20, 200*self.scale.x,
                                 self.batch, self.window,
                                 font_name=font, font_size=20*self.scale.x,
                                 bold=False, anchor_x='left',
                                 anchor_y='center')
        self.widget.set_focus(None)
        self.collabel = Label('color', font_name=font,
                              font_size=24*self.scale.x, bold=False,
                              x=200*self.scale.x, y=400*self.scale.y,
                              anchor_x='left', anchor_y='center',
                              batch=self.batch)
        #color checkboxes
        for i, a in enumerate(options.colors.iteritems()):
            key, val = a
            x = (i*70 + 500) * self.scale.x
            y = (380) * self.scale.y
            self.layout.actives[key] = ccb([x, y], self.batch, val,
                                           size=[40*self.scale.x]*2)
            if key == self.options['color']:
                self.layout.actives[key].activate()
        self.activecolor = None

    def add_update(self, dt):
        if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
            self.send_message('menu_transition_-')

        if (self.keys[key.ENTER]
                and not self.keys_old[key.ENTER]) and (
                self.widget.focus and len(self.widget.document.text) > 0):
            if len(self.widget.document.text.strip()) > 0:
                self.widget.set_focus(None)
                name = self.widget.document.text.strip()
                self.options['name'] = name

        if self.widget.focus:
                name = self.widget.document.text.strip()
                self.options['name'] = name

    def handle_clicks(self, key):
        if not key in options.colors:
            self.widget.remove_handler()
        if key == 'cancel':
            self.send_message('menu_transition_-')
        elif key == 'save':
            name = self.widget.document.text.strip()
            self.options['name'] = name
            if self.activecolor:
                self.options['color'] = self.activecolor
            self.options.save()
            self.send_message('options')
            self.send_message('menu_transition_-')
        elif key in options.colors:
            self.layout.actives[key].activate()
            self.activecolor = key
            self.options['color'] = self.activecolor
            for key_ in self.layout.actives:
                if key_ in options.colors and not key == key_:
                    self.layout.actives[key_].deactivate()
        elif key == 'keys':
            self.send_message('switch_to', (KeyMapMenu,
                              (self.window, self.options)))
        elif key == 'graphics':
            self.send_message('switch_to', (GraphicsMenu,
                              (self.window, self.options)))


class KeyMapMenu(MenuClass):
    """docstring for KeyMapMenu"""
    def __init__(self, arg, *args, **kwargs):
        super(KeyMapMenu, self).__init__(*args, **kwargs)
        try:
            self.window, self.options = arg
        except TypeError:
            self.window = arg
            self.options = options.Options()
        self.layout.add_headline('options')
        self.layout.add_bottom([('cancel',)*2, ('save',)*2])
        self.layout.add_tabs([('player', 'player'), ('keys', 'controls', 1),
                             ('graphics',)*2])
        self.layout.actives['test'] = KeysFrame([390, 600], 500, 430,
                                                self.window, self.batch,
                                                line_space=15, scl=self.scale)
        for i, a in enumerate(chain(*(inputdict.iteritems(),
                              weaponsdict.iteritems()))):
            ke, val = a
            key = self.options[ke]
            self.layout.actives['test'].insert(ke, key)

    def handle_clicks(self, key):
        if key == 'cancel':
            self.layout.actives['test'].remove_handler()
            self.send_message('menu_transition_-')
        elif key == 'test':
            if not self.layout.actives['test'].active_line:
                self.keys_old[1338] = True
            self.layout.actives['test'].activate()
        if key == 'save':
            self.options.save()
            self.send_message('options')
            self.layout.actives['test'].remove_handler()
            self.send_message('menu_transition_-')
        elif key == 'player':
            self.layout.actives['test'].remove_handler()
            self.send_message('switch_to', (PlayerOptions,
                              (self.window, self.options)))
        elif key == 'graphics':
            self.layout.actives['test'].remove_handler()
            self.send_message('switch_to', (GraphicsMenu,
                              (self.window, self.options)))

    def add_update(self, dt):
        if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
            self.layout.actives['test'].deactivate()
        else:
            if self.layout.actives['test'].active_line:
                keys = [ky for ky, val in self.keys.iteritems() if val is
                        True and self.keys_old[ky] is not True]
                if keys:
                    k = keys[0]
                    if k != 1338:
                        newkey = key.symbol_string(k)
                    else:
                        newkey = 'M1'
                    if newkey in self.options:
                        self.layout.actives['test'].deactivate()
                        return
                    val = self.layout.actives['test'].get_action()
                    gen = chain(*(inputdict.iteritems(),
                                weaponsdict.iteritems()))
                    try:
                        corr_key = [k for k, va in gen if va == val][0]
                    except:
                        print val
                    self.options[corr_key] = newkey
                    gen = chain(*(inputdict.iteritems(),
                                weaponsdict.iteritems()))

                    view = self.layout.actives['test'].layout.view_y
                    self.layout.actives['test'] = KeysFrame([390, 600],
                          500, 330, self.window, self.batch, line_space=15)
                    for i, a in enumerate(chain(*(inputdict.iteritems(),
                                          weaponsdict.iteritems()))):
                        ke, val = a
                        ky = self.options[ke]
                        self.layout.actives['test'].insert(ke, ky)
                    self.layout.actives['test'].layout.view_y = view
                    self.layout.actives['test'].layout.x *= self.scale.x
                    self.layout.actives['test'].layout.y *= self.scale.y


class GraphicsMenu(MenuClass):
    """docstring for GraphicsMenu"""
    def __init__(self, arg, *args, **kwargs):
        super(GraphicsMenu, self).__init__(*args, **kwargs)
        try:
            self.window, self.options = arg
        except TypeError:
            self.window = arg
            self.options = options.Options()
        self.layout.add_headline('options')
        self.layout.add_bottom([('cancel',)*2, ('save',)*2])
        self.layout.add_tabs([('player', 'player'), ('keys', 'controls'),
                             ('graphics',)*3])

        #window mode
        self.windowmode = Label('window mode', font_name=font,
                                font_size=22*self.scale.x, bold=False,
                                x=200*self.scale.x, y=500*self.scale.y,
                                anchor_x='left', anchor_y='center',
                                batch=self.batch)

        text = self.options['wmode']
        btn = PopMenu(text, wmodes, [500, 500], self.window,
                      self.batch, 15, 22, scl=self.scale)
        self.layout.actives['wmode'] = btn

        #vsync
        self.vsync = Label('vsync', font_name=font,
                           font_size=22*self.scale.x, bold=False,
                           x=200*self.scale.x, y=400*self.scale.y,
                           anchor_x='left', anchor_y='center',
                           batch=self.batch)

        text = 'On' if self.options['vsync'] != '0' else 'Off'
        btn = PopMenu(text, ['On', 'Off'], [500, 400], self.window,
                      self.batch, 15, 22, scl=self.scale)
        self.layout.actives['vsync'] = btn

    def handle_clicks(self, key):
        if key == 'cancel':
            self.send_message('menu_transition_-')
        if key == 'save':
            self.options.save()
            self.send_message('options')
            self.send_message('menu_transition_-')
        elif key == 'player':
            self.send_message('switch_to', (PlayerOptions,
                              (self.window, self.options)))
        elif key == 'keys':
            self.send_message('switch_to', (KeyMapMenu,
                              (self.window, self.options)))
        elif key == 'wmode':
            rtn = self.layout.actives[key].activate()
            if rtn:
                self.options['wmode'] = rtn
        elif key == 'vsync':
            rtn = self.layout.actives[key].activate()
            if rtn:
                rtn = '0' if rtn == 'Off' else '1'
                self.options['vsync'] = rtn

    def handle_empty(self):
        for item in self.layout.actives.itervalues():
            if isinstance(item, PopMenu):
                item.deactivate()
