# file for all the screens in the game
from graphics import Camera
from player import player


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
