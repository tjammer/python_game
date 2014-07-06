from screens import GameScreen, MainMenu, LoadScreen
from player.controls import InputHandler
from graphics.primitives import CrossHair
from menu_events import Events
from network_utils import protocol_pb2 as proto


class WindowManager(Events):
    """docstring for WindowManager"""
    def __init__(self, window):
        super(WindowManager, self).__init__()
        self.window = window
        self.InputHandler = InputHandler(self.window)
        self.window.push_handlers(self.InputHandler.keys)
        self.stack = []
        self.cross = CrossHair()
        self.saved_mouse = (1280 / 2, 720 / 2)

        # set up main menu as starting screen
        self.current_screen = MainMenu()
        self.register_screen()

        """@self.window.event
        def on_resize(width, height):
            if isinstance(self.current_screen, GameScreen):
                self.current_screen.camera.on_resize(width, height)
            self.InputHandler.on_resize(width, height)"""

    def update(self, dt):
        self.InputHandler.process_keys(dt)
        if (self.stack[0] != self.current_screen and
                isinstance(self.stack[0], GameScreen)):
            self.stack[0].send_to_client(dt)
        self.current_screen.update(dt)

    def draw(self):
        # stack[0] is gamescreen
        if self.stack[0] != self.current_screen:
            self.stack[0].draw()
        self.current_screen.draw()
        self.cross.draw(*self.InputHandler.mousepos)

    # receive events, a lot of transitions will happen here
    def receive_events(self, event, msg):
        if event == 'kill_self':
            from twisted.internet import reactor
            reactor.stop()

        elif event == 'start_game':
            self.stack = []
            self.start_game()

        elif event == 'to_main':
            self.stack = []
            self.current_screen = MainMenu()
            self.register_screen()
            self.disconnect()

        elif event == 'menu_transition_+':
            if isinstance(self.current_screen, GameScreen):
                self.saved_mouse = tuple(self.InputHandler.mousepos)
                self.current_screen.player.input = proto.input()
            self.current_screen = msg()
            self.register_screen()

        elif event == 'menu_transition_-':
            self.stack.pop()
            self.current_screen = self.stack[-1]
            self.register_screen()

        # input to client
        elif event == 'input':
            self.send_message('input', msg)

        # server plaerdata
        elif event == 'serverdata':
            if isinstance(self.stack[0], GameScreen):
                self.stack[0].from_server(msg)

        elif event == 'on_connect':
            self.stack[0].on_connect(msg)
            self.current_screen.on_connect()

    def start_game(self):
        self.current_screen = GameScreen(self.window)
        self.register_screen()
        #get to load screen
        self.receive_events('menu_transition_+', LoadScreen)
        self.connect()

    def register_screen(self):
        # menu screen
        if not isinstance(self.current_screen, GameScreen):
            self.InputHandler.register(self.current_screen.receive_event,
                                       events=('changed_mouse', 'all_input'))
        # game screen
        else:
            for i, j in enumerate(self.saved_mouse):
                self.InputHandler.mousepos[i] = j

            self.InputHandler.register(self.current_screen.camera.
                                       receive_m_pos, 'changed_mouse')

            # set mouse on same position as it was before opening menu
            self.InputHandler.send_message('changed_mouse',
                                           self.InputHandler.mousepos)
            # pass by ref bullshit
            self.current_screen.player.input = self.InputHandler.directns
            self.current_screen.controls = self.InputHandler.controls
            # sends player input to lient class
            self.current_screen.register(self.receive_events, 'input')
            self.current_screen.camera.register(self.InputHandler.receive_aim,
                                                'mousepos')

        self.current_screen.register(self.receive_events)
        self.stack.append(self.current_screen)

    def input_to_client(self):
        pass
