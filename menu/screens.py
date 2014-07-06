# file for all the screens in the game
from graphics.camera import Camera
from player import player
from elements import TextBoxFramed as btn
from menu_events import Events, MenuClass
from pyglet.text import Label
from graphics.primitives import Box
from pyglet.window import key
from maps.map import Map
from network_utils.clientclass import move, moves, correct_client
from network_utils import protocol_pb2 as proto


class GameScreen(Events):
    """docstring for GameScreen"""
    def __init__(self, window):
        super(GameScreen, self).__init__()
        self.camera = Camera(window)
        self.player = player.Player()
        self.controls = {}
        self.controls_old = {}
        self.map = Map('testmap')
        #self.player.spawn(100, 100)
        self.time = 0
        self.moves = moves(1024)
        self.index = [0]
        self.head = [0]
        #other players
        self.players = {}

    def update(self, dt):
        dt = int(dt * 10000) / 10000.
        self.update_physics(dt)
        self.camera.update(dt, self.player.state)
        self.send_to_client(dt)

        if self.controls['esc'] and not self.controls_old['esc']:
            self.send_message('menu_transition_+', GameMenu)

        for key_, value in self.controls.items():
            self.controls_old[key_] = value

    def update_physics(self, dt, state=False, input=False):
        self.player.update(dt, state, input)
        # for rect in self.map.rects:
        for rect in self.map.quad_tree.retrieve([], self.player.rect):
            coll = self.player.rect.collides(rect)
            if coll:
                ovr, axis = coll
                self.player.resolve_collision(ovr, axis, rect.angle)
        return self.player.state

    def from_server(self, data):
        typ, data = data
        if typ == proto.update:
            ind, time, s_state = data
            smove = move(time, None, s_state)
            if ind == self.player.id:
                correct_client(self.update_physics, smove, self.moves,
                               self.head, self.index[0])
            else:
                self.players[ind].client_update(s_state)
        elif typ == proto.newplayer:
            print 'new player'
            ind, time, s_state = data
            self.players[ind] = player.Player()
            self.players[ind].state = s_state
        elif typ == proto.disconnect:
            ind = data
            del self.players[ind]

    def send_to_client(self, dt):
        self.time += int(dt * 10000)
        c_move = move(self.time, self.player.input, self.player.state.copy())
        try:
            self.moves[self.index[0]] = c_move
        except IndexError:
            self.moves.append(c_move)
        self.moves.advance(self.index)
        self.send_message('input', (self.player.input, self.time))

    def draw(self):
        self.camera.set_camera()
        for plr in self.players.itervalues():
            plr.draw()
        self.player.draw()
        self.map.draw()
        self.camera.set_static()

    def on_connect(self, msg):
        self.player.get_id(msg)
        print 'connected with id: ' + str(self.player.id)


class MainMenu(MenuClass):
    """docstring for MainMenu"""
    def __init__(self):
        super(MainMenu, self).__init__()
        self.buttons['start'] = btn([500, 400], 'start game')
        self.buttons['quit'] = btn([500, 200], 'quit game')

    def handle_clicks(self, key):
        if key == 'quit':
            self.send_message('menu_transition_+', QuitScreen)
        if key == 'start':
            self.send_message('start_game')


class QuitScreen(MenuClass):
    """docstring for QuitScreen"""
    def __init__(self):
        super(QuitScreen, self).__init__()
        self.buttons['quit'] = btn([300, 300], 'yes')
        self.buttons['dont_quit'] = btn([680, 300], 'no')
        self.text = 'do you really want to quit?'
        self.Label = Label(self.text, font_name='Helvetica',
                           font_size=36, bold=False,
                           x=640,
                           y=500,
                           anchor_x='center', anchor_y='center')
        self.Box = Box([340, 200], [600, 400], 2)

    def handle_clicks(self, key):
        if key == 'quit':
            self.send_message('kill_self')
        if key == 'dont_quit':
            self.send_message('menu_transition_-')

    def draw(self):
        self.Box.draw()
        for key_, panel in self.buttons.iteritems():
            panel.draw()
        self.Label.draw()


class GameMenu(MenuClass):
    """docstring for GameMenu
    main menu ingame"""
    def __init__(self):
        super(GameMenu, self).__init__()
        self.buttons['resume'] = btn([500, 400], 'resume game')
        self.buttons['to_main'] = btn([500, 200], 'main menu')

    def handle_clicks(self, key):
        if key == 'resume':
            self.send_message('menu_transition_-')

        if key == 'to_main':
            self.send_message('to_main')

    def add_update(self):
        try:
            if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
                self.send_message('menu_transition_-')
        except:
            pass


class LoadScreen(MenuClass):
    """docstring for LoadScreen"""
    def __init__(self):
        super(LoadScreen, self).__init__()
        self.label = Label('connecting to server', font_name='Helvetica',
                           font_size=36, bold=False, x=200, y=550,
                           anchor_x='left', anchor_y='baseline')

    def draw(self):
        self.label.draw()

    def on_connect(self):
        self.send_message('menu_transition_-')

    def add_update(self):
        if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
            self.send_message('to_main')
