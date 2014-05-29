from screens import GameScreen, MainMenu
from player.controls import InputHandler
from graphics.primitives import CrossHair
from menu_events import Events


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

    def update(self, dt):
        self.InputHandler.process_keys(dt)
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

        if event == 'start_game':
            self.stack = []
            self.start_game()

        if event == 'to_main':
            self.stack = []
            self.current_screen = MainMenu()
            self.register_screen()

        if event == 'menu_transition_+':
            if isinstance(self.current_screen, GameScreen):
                self.saved_mouse = tuple(self.InputHandler.mousepos)
            self.current_screen = msg()
            self.register_screen()

        if event == 'menu_transition_-':
            self.stack.pop()
            self.current_screen = self.stack[-1]
            self.register_screen()

        # input to client
        if event == 'input':
            self.send_message('input', msg)

        # server plaerdata
        if event == 'serverdata':
            if isinstance(self.stack[0], GameScreen):
                # self.stack[0].Player.pos = [msg.posx, msg.posy]
                # self.stack[0].Player.vel = [msg.velx, msg.vely]
                self.stack[0].Player.client_update(msg)

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
            for i, j in enumerate(self.saved_mouse):
                self.InputHandler.mousepos[i] = j

            self.InputHandler.register(self.current_screen.Camera.
                                       receive_m_pos, 'changed_mouse')

            # set mouse on same position as it was before opening menu
            self.InputHandler.send_message('changed_mouse',
                                           self.InputHandler.mousepos)
            # pass by ref bullshit
            self.current_screen.Player.input = self.InputHandler.directns
            self.current_screen.controls = self.InputHandler.controls
            # sends player input to lient class
            self.current_screen.register(self.receive_events, 'input')

        self.current_screen.register(self.receive_events)
        self.stack.append(self.current_screen)

    def input_to_client(self):
        pass
