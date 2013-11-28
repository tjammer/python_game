# file for all the screens in the game
from graphics.camera import Camera
from player import player
from elements import TextBoxFramed
from menu_events import Events


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

    def update(self, dt):
        self.Player.update(dt)
        self.Camera.update(dt)
        if self.controls['esc']:
            self.send_message('menu_transition_+', GameMenu)

    def draw(self):
        self.Camera.set_camera()
        self.Player.draw()
        self.Camera.set_static()


class MenuClass(object):
    """docstring for MenuClass
    base class for other menus to inherit from"""
    def __init__(self):
        super(MenuClass, self).__init__()
        self.buttons = {}
        self.text_boxes = {}
        self.m_pos = [0, 0]
        self.keys = {}
        self.listeners = {}

    def update(self, dt):
        for key, button in self.buttons.items():
            if button.in_box(self.m_pos):
                button.Box.highlight()
                try:
                    if self.keys[1338]:
                        self.handle_clicks(key)
                except KeyError:
                    continue
            else:
                button.Box.restore()

    def draw(self):
        for key, button in self.buttons.items():
            button.draw()
        for key, box in self.text_boxes.items():
            box.draw()

    def handle_clicks(self, key):
        pass

    # receive events
    def receive_event(self, event, msg):
        if event == 'changed_mouse':
            self.m_pos = msg
        if event == 'all_input':
            self.keys = msg

    # send events
    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg=None):
        for listener, events in self.listeners.items():
            try:
                listener(event, msg)
            except (Exception, ):
                self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]


class MainMenu(MenuClass):
    """docstring for MainMenu"""
    def __init__(self):
        super(MainMenu, self).__init__()
        self.buttons['start'] = TextBoxFramed([500, 400], 'start game')
        self.buttons['quit'] = TextBoxFramed([500, 200], 'quit game')

    def handle_clicks(self, key):
        if key == 'quit':
            self.send_message('kill_self')
        if key == 'start':
            self.send_message('start_game')


class GameMenu(MenuClass):
    """docstring for GameMenu
    main menu ingame"""
    def __init__(self):
        super(GameMenu, self).__init__()
        self.buttons['resume'] = TextBoxFramed([500, 400], 'resume game')
        self.buttons['to_main'] = TextBoxFramed([500, 200], 'to main menu')

    def handle_clicks(self, key):
        if key == 'resume':
            self.send_message('resume')
