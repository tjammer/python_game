from screens import GameScreen, MainMenu
from player.controls import InputHandler
from graphics.primitives import Cross


class WindowManager(object):
    """docstring for WindowManager"""
    def __init__(self, window):
        super(WindowManager, self).__init__()
        self.window = window
        self.current_screen = MainMenu()
        self.InputHandler = InputHandler(self.window)
        self.window.push_handlers(self.InputHandler.keys)
        # get mouse position and clicks to menu
        self.InputHandler.register(self.current_screen.receive_event,
                                   events=('changed_mouse', 'all_input'))
        # receive all events from currentscreen
        self.current_screen.register(self.receive_events)
        # dont forget to unregister while changing menus
        self.cursor = Cross()

    def update(self, dt):
        self.InputHandler.process_keys()
        self.current_screen.update(dt)

    def draw(self):
        self.current_screen.draw()
        # draw cursor
        self.cursor.draw(*self.InputHandler.mousepos)

    # receive events, a lot of transitions will happen here
    def receive_events(self, event, msg):
        if event == 'kill_self':
            import pyglet
            pyglet.app.exit()
        if event == 'start_game':
            pass
            # self.start_game()

    # methods for behaviour for transitions
    def start_game(self):
        self.current_screen = GameScreen(self.window)
        self.InputHandler.register(self.current_screen.Camera.receive_m_pos,
                                   'changed_mouse')
