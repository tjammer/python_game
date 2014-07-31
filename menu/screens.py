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
from gameplay.weapons import ProjectileViewer
from itertools import chain
from graphics.primitives import CrossHair
from hud import Hud
from gameplay.gamestate import GameStateViewer


class GameScreen(Events):
    """docstring for GameScreen"""
    def __init__(self, window):
        super(GameScreen, self).__init__()
        self.camera = Camera(window)
        self.player = player.Player()
        self.proj_viewer = ProjectileViewer()
        self.controls = {}
        self.controls_old = {}
        self.map = Map('newtest')
        #self.player.spawn(100, 100)
        self.time = 0
        self.moves = moves(1024)
        self.index = [0]
        self.head = [0]
        #other players
        self.players = {}
        self.specs = {}
        #crosshair
        self.cross = CrossHair()
        self.isSpec = True
        self.hud = Hud()
        self.gs_view = GameStateViewer(self.players, self.hud.update_prop,
                                       self.hud.set_score)

    def update(self, dt):
        dt = int(dt * 10000) / 10000.
        if self.controls['esc'] and not self.controls_old['esc']:
            self.send_message('menu_transition_+', GameMenu)

        for key_, value in self.controls.items():
            self.controls_old[key_] = value
        self.on_update(dt)

    def update_physics(self, dt, state=False, input=False):
        playergen = (player.rect for player in self.players.itervalues())
        mapgen = (rect for rect in self.map.quad_tree.retrieve([],
                  self.player.rect))
        rectgen = chain(playergen, mapgen)
        self.player.update(dt, rectgen, state, input)
        return self.player.state

    def from_server(self, data):
        typ, data = data
        if typ == proto.playerUpdate:
            ind, time, s_state = data
            smove = move(time, None, s_state)
            if ind == self.player.id:
                try:
                    correct_client(self.update_physics, smove, self.moves,
                                   self.head, self.index[0])
                except IndexError:
                    pass
            else:
                #try:
                self.players[ind].client_update(s_state)
                #except KeyError:
                #    pass
        elif typ == proto.projectile:
            self.proj_viewer.process_proj(data)
        elif typ == proto.newPlayer:
            gs, data = data
            if gs == proto.goesSpec:
                ind, name = data
                new = player.Player()
                new.name = name
                new.id = ind
                self.specs[ind] = new
            #if there are existing players on the server
            elif gs == proto.wantsJoin:
                ind, name, state, time = data
                new = player.Player()
                new.name = name
                new.state = state
                new.time = time
                new.id = ind
                self.players[ind] = new
                print 'new player: %s' % name
                self.gs_view.to_team(ind)
        elif typ == proto.disconnect:
            ind = data
            if ind in self.players:
                self.gs_view.leave(ind)
                del self.players[ind]
            elif ind in self.specs:
                del self.specs[ind]
        elif typ == proto.stateUpdate:
            gametime, data = data
            gs, ind = data
            self.gs_view.set_time(gametime)
            if gs == proto.wantsJoin:
                if ind == self.player.id:
                    self.send_message('menu_transition_-')
                    self.player.state.isDead = False
                    self.trans_to_game()
                else:
                    self.players[ind] = self.specs[ind]
                    del self.specs[ind]
                    self.gs_view.to_team(ind)
            elif gs == proto.goesSpec:
                if ind == self.player.id and self.isSpec:
                    pass
                elif ind == self.player.id and not self.isSpec:
                    self.send_message('menu_transition_-')
                    self.trans_to_spec()
                else:
                    self.specs[ind] = self.players[ind]
                    self.gs_view.leave(ind)
                    del self.players[ind]
            elif gs == proto.isDead:
                ind, killer, weapon = ind
                if ind == self.player.id:
                    self.player.die()
                    self.player.rect.update_color((.5, .5, .5))
                else:
                    self.players[ind].die()
                    self.players[ind].rect.update_color((.5, .5, .5))
                self.gs_view.score(ind, killer, weapon)
            elif gs == proto.spawns:
                ind, pos = ind
                if ind == self.player.id:
                    self.player.spawn(*pos)
                else:
                    self.players[ind].spawn(*pos)

    def send_to_client(self, dt):
        temp_input = proto.Input()
        self.time += int(dt * 10000)
        temp_input.CopyFrom(self.player.input)
        c_move = move(self.time, temp_input, self.player.state.copy())
        try:
            self.moves[self.index[0]] = c_move
        except IndexError:
            self.moves.append(c_move)
        self.moves.advance(self.index)
        self.send_message('input', (self.player.input, self.time))

    def draw(self):
        self.on_draw()

    def on_connect(self, msg):
        ind, mapname = msg
        self.player.get_id(ind)
        self.map = Map(mapname)
        print 'connected with id: ' + str(self.player.id)
        #self.send_message('input', (self.player.input, 1337))
        self.gs_view.init_self(ind)
        self.trans_to_spec()

    def try_join(self):
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = self.player.id
        msg.player.CopyFrom(plr)
        if self.isSpec:
            msg.gameState = proto.wantsJoin
        else:
            msg.gameState = proto.goesSpec
        self.send_message('other', msg)

    def on_update(self, dt):
        pass

    def on_draw(self):
        pass

    def idle_update(self, dt):
        self.send_to_client(dt)
        self.gs_view.update(dt)
        self.hud.update(dt)

    def trans_to_spec(self):
        self.on_update = self.spec_update
        self.on_draw = self.spec_draw
        self.isSpec = True

    def trans_to_game(self):
        self.on_update = self.game_update
        self.on_draw = self.game_draw
        self.isSpec = False
        self.player.weapons.hook_hud(self.hud.update_prop)
        self.player.state.hook_hud(self.hud.update_prop)
        self.gs_view.add_self(self.player)
        self.hud.init_player(self.players)

    def game_update(self, dt):
        self.update_physics(dt)
        self.camera.update(dt, self.player.state)
        self.send_to_client(dt)
        self.proj_viewer.update(dt)
        self.gs_view.update(dt)
        self.hud.update(dt)

    def game_draw(self):
        self.camera.set_camera()
        for plr in self.players.itervalues():
            plr.draw()
        self.player.draw()
        self.proj_viewer.draw()
        self.map.draw()
        self.camera.set_static()
        self.hud.draw()
        self.cross.draw(*self.camera.mpos)

    def spec_update(self, dt):
        self.player.specupdate(dt)
        self.camera.update(dt, self.player.state)
        self.send_to_client(dt)
        self.proj_viewer.update(dt)
        self.gs_view.update(dt)

    def spec_draw(self):
        self.camera.set_camera()
        for plr in self.players.itervalues():
            plr.draw()
        self.proj_viewer.draw()
        self.map.draw()
        self.camera.set_static()


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
    def __init__(self, *args, **kwargs):
        super(GameMenu, self).__init__(*args, **kwargs)
        self.buttons['resume'] = btn([500, 400], 'resume game')
        self.buttons['to_main'] = btn([500, 200], 'main menu')
        if self.bool:
            self.buttons['join_game'] = btn([950, 50], 'join game')
        else:
            self.buttons['join_game'] = btn([950, 50], 'spectate')
        self.cd = 0

    def handle_clicks(self, key):
        if key == 'resume':
            self.send_message('menu_transition_-')

        if key == 'to_main':
            self.send_message('to_main')

        if key == 'join_game' and not self.cd:
            self.send_message('try_join')
            self.cd = 1

    def add_update(self, dt):
        if self.cd:
            self.cd -= dt
            if self.cd < 0:
                self.cd = 0
        try:
            if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
                self.send_message('menu_transition_-')
        except:
            pass


class LoadScreen(MenuClass):
    """docstring for LoadScreen"""
    def __init__(self, *args, **kwargs):
        super(LoadScreen, self).__init__(*args, **kwargs)
        self.label = Label('connecting to server', font_name='Helvetica',
                           font_size=36, bold=False, x=200, y=550,
                           anchor_x='left', anchor_y='baseline')

    def draw(self):
        self.label.draw()

    def on_connect(self):
        self.send_message('menu_transition_-')

    def add_update(self, dt):
        try:
            if self.keys[key.ESCAPE] and not self.keys_old[key.ESCAPE]:
                self.send_message('to_main')
        except:
            pass
