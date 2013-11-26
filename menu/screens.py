# file for all the screens in the game
from graphics.camera import Camera
from player import player
from elements import TextBoxFramed


class GameScreen(object):
    """docstring for GameScreen"""
    def __init__(self, window):
        super(GameScreen, self).__init__()
        self.Camera = Camera(window)
        self.Player = player.player()
        # register camera with player for tracking playermovement
        self.Player.register(self.Camera.receive_player_pos,
                             events='changed_pos')

    def update(self, dt):
        self.Player.update(dt)
        self.Camera.update(dt)


class MainMenu(object):
    """docstring for MainMenu"""
    def __init__(self):
        super(MainMenu, self).__init__()
        self.buttons = {}
        self.buttons['start'] = TextBoxFramed([500, 400], 'start game')
        self.buttons['quit'] = TextBoxFramed([500, 200], 'quit game')
        self.m_pos = [0, 0]

    def update(self, dt):
        for key, button in self.buttons.items():
            if button.in_box(self.m_pos):
                button.Box.highlight()
            else:
                button.Box.restore()

    def draw(self):
        for key, button in self.buttons.items():
            button.draw()

    def receive_mouse_pos(self, event, m_pos):
        self.m_pos = m_pos
