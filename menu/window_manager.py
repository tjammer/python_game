from screens import GameScreen, MainMenu
from controls import InputHandler


class WindowManager(object):
    """docstring for WindowManager"""
    def __init__(self, window):
        super(WindowManager, self).__init__()
        self.window = window
        self.current_screen = MainMenu()
        self.InputHandler = InputHandler(self.window)
        self.window.push_handlers(self.InputHandler.keys)
        # get mouse position to menu
        self.InputHandler.register(self.current_screen.receive_mouse_pos,
                                   events='changed mouse')
        # dont forget to unregister while changing menus

    def update(self, dt):
        self.InputHandler.process_keys()
        self.current_screen.update(dt)
