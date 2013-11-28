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
        # when ingame keeps track of the number of menus open
        self.stack = []
        # get mouse position and clicks to menu
        self.InputHandler.register(self.current_screen.receive_event,
                                   events=('changed_mouse', 'all_input'))
        # receive all events from current_screen
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
            # pass
            self.start_game()
        if event == 'menu_transition_+':
            self.stack.append(self.current_screen)
            self.current_screen = msg()
            self.register_screen()
            print self.current_screen

    # methods for behaviour for transitions
    def start_game(self):
        self.current_screen = GameScreen(self.window)
        self.register_screen()

    def register_screen(self):
        # menu screen
        if not isinstance(self.current_screen, GameScreen):
            self.InputHandler.register(self.current_screen.receive_event,
                                       events=('changed_mouse', 'all_input'))
        # game screen
        else:
            self.InputHandler.register(self.current_screen.Camera.
                                       receive_m_pos, 'changed_mouse')
            # pass by ref bullshit
            self.current_screen.Player.Move.input = self.InputHandler.directns
            self.current_screen.controls = self.InputHandler.controls
        self.current_screen.register(self.receive_events)
