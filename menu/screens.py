# file for all the screens in the game
from graphics.camera import Camera
from player import player
from elements import TextBoxFramed
from menu_events import Events, MenuClass


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
        self.buttons['to_main'] = TextBoxFramed([500, 200], 'main menu')

    def handle_clicks(self, key):
        if key == 'resume':
            self.send_message('menu_transition_-')

        if key == 'to_main':
            self.send_message('to_main')
