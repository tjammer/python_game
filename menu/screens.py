# file for all the screens in the game
from graphics.camera import Camera
from player import player
from elements import TextBoxFramed as btn
from menu_events import Events, MenuClass
from pyglet.text import Label
from graphics.primitives import Box
from pyglet.window import key
from maps.map import Map


class GameScreen(Events):
    """docstring for GameScreen"""
    def __init__(self, window):
        super(GameScreen, self).__init__()
        self.Camera = Camera(window)
        self.Player = player.player()
        # register camera with player for tracking playermovement
        self.Player.register(self.Camera.receive_player_pos,
                             events='changed_pos')
        self.controls = {}
        self.controls_old = {}
        self.Map = Map('testmap')
        self.Player.spawn(100, 100)

    def update(self, dt):
        self.Player.update(dt)
        self.Camera.update(dt)
        if self.controls['esc'] and not self.controls_old['esc']:
            self.send_message('menu_transition_+', GameMenu)

        # for rect in self.Map.rects:
        for rect in self.Map.quad_tree.retrieve([], self.Player.Rect):
            coll = self.Player.Rect.collides(rect)
            if coll:
                ovr, axis = coll
                self.Player.resolve_collision(ovr, axis, rect.angle)

        for key_, value in self.controls.items():
            self.controls_old[key_] = value

    def draw(self):
        self.Camera.set_camera()
        self.Player.draw()
        self.Map.draw()
        self.Camera.set_static()


class MainMenu(MenuClass):
    """docstring for MainMenu"""
    def __init__(self):
        super(MainMenu, self).__init__()
        self.buttons['start'] = btn([500, 400], 'start game')
        self.buttons['quit'] = btn([500, 200], 'quit game')

    def handle_clicks(self, key):
        if key == 'quit':
            self.send_message('menu_transition_+', QuitScreen)
        if key == 'start':
            self.send_message('start_game')


class QuitScreen(MenuClass):
    """docstring for QuitScreen"""
    def __init__(self):
        super(QuitScreen, self).__init__()
        self.buttons['quit'] = btn([300, 300], 'yes')
        self.buttons['dont_quit'] = btn([680, 300], 'no')
        self.text = 'do you really want to quit?'
        self.Label = Label(self.text, font_name='Helvetica',
                           font_size=36, bold=False,
                           x=640,
                           y=500,
                           anchor_x='center', anchor_y='center')
        self.Box = Box([340, 200], [600, 400], 2)

    def handle_clicks(self, key):
        if key == 'quit':
            self.send_message('kill_self')
        if key == 'dont_quit':
            self.send_message('menu_transition_-')

    def draw(self):
        self.Box.draw()
        for key_, panel in self.buttons.iteritems():
            panel.draw()
        self.Label.draw()


class GameMenu(MenuClass):
    """docstring for GameMenu
    main menu ingame"""
    def __init__(self):
        super(GameMenu, self).__init__()
        self.buttons['resume'] = btn([500, 400], 'resume game')
        self.buttons['to_main'] = btn([500, 200], 'main menu')

    def handle_clicks(self, key):
        if key == 'resume':
            self.send_message('menu_transition_-')

        if key == 'to_main':
            self.send_message('to_main')

    def add_update(self):
        try:
            if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
                self.send_message('menu_transition_-')
        except:
            pass
