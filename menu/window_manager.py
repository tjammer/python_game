from screens import MainMenu, LoadScreen
from player.controls import InputHandler
from menu_events import Events
from network_utils import protocol_pb2 as proto
from gamescreen import GameScreen


class WindowManager(Events):
    """docstring for WindowManager"""
    def __init__(self, window):
        super(WindowManager, self).__init__()
        self.window = window
        self.InputHandler = InputHandler(self.window)
        self.window.push_handlers(self.InputHandler.keys)
        self.stack = []
        #self.cross = CrossHair()
        self.saved_mouse = (1280 / 2, 720 / 2)

        # set up main menu as starting screen
        self.current_screen = MainMenu(window=self.window)
        self.register_screen()

    def update(self, dt):
        self.InputHandler.process_keys(dt)
        if (self.stack[0] != self.current_screen and
                isinstance(self.stack[0], GameScreen)):
            self.stack[0].idle_update(dt)
        self.current_screen.update(dt)

    def draw(self):
        # stack[0] is gamescreen
        if self.stack[0] != self.current_screen:
            if isinstance(self.stack[0], GameScreen):
                self.stack[0].draw()
        self.current_screen.draw()

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
            self.current_screen = MainMenu(window=self.window)
            self.register_screen()
            self.disconnect()
            self.saved_mouse = (1280 / 2, 720 / 2)

        elif event == 'menu_transition_+':
            msg, arg = msg
            if isinstance(self.current_screen, GameScreen):
                self.saved_mouse = tuple(self.InputHandler.m_cam)
                #save aimpos, otherwise 0, 0 is sent to server
                #and viewed by specs
                inpt = proto.Input()
                inpt.mx = self.current_screen.player.input.mx
                inpt.my = self.current_screen.player.input.my
                self.current_screen.player.input = inpt
                try:
                    self.InputHandler.unregister(self.current_screen.camera.
                                                 receive_m_pos, 'mouse_cam')
                except KeyError:
                    pass
            self.current_screen = msg(arg, window=self.window)
            self.register_screen()

        elif event == 'menu_transition_-':
            self.stack.pop()
            self.current_screen = self.stack[-1]
            if isinstance(self.current_screen, MainMenu):
                self.current_screen = MainMenu(window=self.window)
            self.register_screen()

        # input to client
        elif event == 'input':
            self.send_message('input', msg)

        elif event == 'other':
            self.send_message('other', msg)

        # server plaerdata
        elif event == 'serverdata':
            if isinstance(self.stack[0], GameScreen):
                self.stack[0].from_server(msg)

        elif event == 'on_connect':
            self.stack[0].on_connect(msg)
            self.current_screen.on_connect()

        elif event == 'try_join':
            self.stack[0].try_join()

        elif event == 'chat':
            self.stack[0].send_chat(msg)

        elif event == 'options':
            self.InputHandler.load_options()

        elif event == 'switch_to':
            msg, arg = msg
            self.stack.pop()
            self.current_screen = msg(arg, window=self.window)
            self.register_screen()

    def start_game(self):
        self.current_screen = GameScreen(self.window, self.InputHandler)
        self.register_screen()
        #get to load screen
        self.receive_events('menu_transition_+', (LoadScreen, False))
        self.connect()

    def register_screen(self):
        # menu screen
        if not isinstance(self.current_screen, GameScreen):
            self.InputHandler.register(self.current_screen.receive_event,
                                       events=('changed_mouse', 'all_input'))
            self.window.set_mouse_visible(True)
            self.window.set_exclusive_mouse(False)
        # game screen
        else:
            for i, j in enumerate(self.saved_mouse):
                self.InputHandler.m_cam[i] = j

            self.InputHandler.register(self.current_screen.camera.
                                       receive_m_pos, 'mouse_cam')

            # set mouse on same position as it was before opening menu
            self.InputHandler.send_message('mouse_cam',
                                           self.InputHandler.m_cam)
            #needed so player doesnt shoot when coming from a menu
            self.InputHandler.keys[1 + self.InputHandler.mouse_offset] = False
            # pass by ref bullshit
            self.current_screen.player.input = self.InputHandler.directns
            self.current_screen.controls = self.InputHandler.controls
            self.current_screen.update_keys()
            # sends player input to lient class
            self.current_screen.register(self.receive_events, 'input')
            self.current_screen.camera.register(self.InputHandler.receive_aim,
                                                'mousepos')
            if not self.current_screen.isSpec:
                self.window.set_mouse_visible(False)
                self.window.set_exclusive_mouse(True)

        self.current_screen.register(self.receive_events)
        self.stack.append(self.current_screen)

    def input_to_client(self):
        pass
