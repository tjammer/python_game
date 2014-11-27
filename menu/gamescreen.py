import pyglet
from graphics.camera import Camera
from player import player
from menu_events import Events
from graphics.primitives import Triangle, AmmoTriangle as Ammo
from maps.map import Map
from network_utils.clientclass import move, moves, correct_client
from network_utils import protocol_pb2 as proto
from graphics.primitives import CrossHair
from hud import Hud
from gameplay.gamestate import GameStateViewer
from graphics.render import Render, ProjectileViewer
from player.cvec2 import cvec2 as vec2
from screens import GameMenu, ChatScreen
from network_utils import timestep


class GameScreen(Events):
    """docstring for GameScreen"""
    def __init__(self, window, input_handler):
        super(GameScreen, self).__init__()
        self.window = window
        self.input_handler = input_handler
        self.camera = Camera(window)
        self.render = Render(self.camera, self.window)
        sc_batch = self.render.scene_batch
        st_batch = self.render.static_batch
        self.player = player.Player(renderhook=self.render.playerhook)
        self.proj_viewer = ProjectileViewer(self.send_center, batch=sc_batch,
                                            scale=self.render.scale)
        self.controls = {}
        self.controls_old = {}
        self.map = Map('blank')
        #self.player.spawn(100, 100)
        self.time = 0
        self.moves = moves(1024)
        self.index = [0]
        self.head = [0]
        #other players
        self.players = {}
        self.specs = {}
        #crosshair
        self.cross = CrossHair(batch=st_batch)
        self.isSpec = 0.5
        self.hud = Hud(batch=st_batch, window=self.window)
        self.gs_view = GameStateViewer(self.players, self.hud.update_prop,
                                       self.hud.set_score)
        self.frozen = False
        self.rest_time = 0

    def update(self, dt):
        dt = int(dt * 1000000.) / 1000000.
        if self.controls['esc'] and not self.controls_old['esc']:
            self.send_message('menu_transition_+', (GameMenu, self.isSpec))

        if self.controls['rdy'] and not self.controls_old['rdy']:
            if not self.isSpec:
                self.ready_up()

        if self.controls['chat'] and not self.controls_old['chat']:
            self.send_message('menu_transition_+',
                              (ChatScreen, None))

        self.update_keys()
        for plr in self.players.itervalues():
            mapgen = [rect for rect in self.map.quad_tree.retrieve([],
                      plr.rect)]
            plr.predict(dt, mapgen)
        self.on_update(dt)

    def update_physics(self, dt, state=False, input=False):
        self.player.update(dt, self.get_rect(), state, input)
        return self.player.state.copy()

    def update_state_only(self, state):
        self.player.state.update_hp(state)

    def update_keys(self):
        for key_, value in self.controls.items():
            self.controls_old[key_] = value

    def from_server(self, data):
        typ, data = data
        if typ == proto.playerUpdate:
            ind, time, s_state, inpt, weaponinfo = data
            smove = move(time, inpt, s_state)
            if ind == self.player.id:
                correct_client(self.update_physics, smove, self.moves,
                               self.head, self.index[0],
                               self.update_state_only)
                self.player.weapons.from_server(weaponinfo)
            else:
                #try:
                self.players[ind].client_update(s_state, self.render.scale)
                self.players[ind].input = inpt
                if ind == self.isSpec:
                    self.camera.mpos_from_aim(vec2(inpt.mx, inpt.my))
                    self.players[ind].weapons.from_server(weaponinfo)
                #except KeyError:
                #    pass
        elif typ == proto.projectile:
            self.proj_viewer.process_proj(data)
        elif typ == proto.newPlayer:
            gs, data = data
            if gs == proto.goesSpec:
                ind, name, colstring = data
                new = player.Player(renderhook=self.render.playerhook, id=ind)
                new.name = name
                new.id = ind
                new.set_color(colstring)
                new.rect.update_color(new.color)
                self.specs[ind] = new
            #if there are existing players on the server
            elif gs == proto.wantsJoin:
                ind, name, state, time, colstring = data
                new = player.Player(renderhook=self.render.playerhook, id=ind)
                new.name = name
                new.state = state
                new.time = time
                new.id = ind
                new.set_color(colstring)
                new.rect.update_color(new.color)
                self.players[ind] = new
                new.add_to_view()
                print 'new player: %s' % name
                self.gs_view.to_team(ind)
        elif typ == proto.disconnect:
            ind = data
            if ind in self.players:
                if ind == self.isSpec:
                    self.cancel_follow()
                self.gs_view.leave(ind)
                self.players[ind].remove_from_view()
                del self.players[ind]
                self.set_playergen()
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
                    if self.isSpec > 0.5:
                        self.players[self.isSpec].state.unhook()
                        self.players[self.isSpec].weapons.unhook()
                    self.trans_to_game()
                else:
                    self.players[ind] = self.specs[ind]
                    del self.specs[ind]
                    self.gs_view.to_team(ind)
                    self.players[ind].add_to_view()
            elif gs == proto.goesSpec:
                if ind == self.player.id and self.isSpec:
                    pass
                elif ind == self.player.id and not self.isSpec:
                    self.send_message('menu_transition_-')
                    self.gs_view.leave(self.player.id)
                    self.trans_to_spec()
                else:
                    self.specs[ind] = self.players[ind]
                    self.gs_view.leave(ind)
                    if ind == self.isSpec:
                        self.cancel_follow()
                    del self.players[ind]
                    self.specs[ind].remove_from_view()
                    self.set_playergen()
            elif gs == proto.isDead:
                ind, killer, weapon = ind
                if ind == self.player.id:
                    self.player.die()
                else:
                    self.players[ind].die()
                self.gs_view.score(ind, killer, weapon)
            elif gs == proto.spawns:
                ind, pos = ind
                if ind == self.player.id:
                    self.player.spawn(*pos)
                else:
                    self.players[ind].spawn(*pos, other=True)
            elif gs == proto.isReady:
                ind, name = ind
                self.gs_view.is_ready(ind, name)
            elif gs == proto.countDown:
                self.player.freeze()
                self.gs_view.count_down()
            elif gs == proto.inProgress:
                self.gs_view.start_game()
            elif gs == proto.warmUp:
                self.frozen = False
                self.gs_view.to_warmup()
            elif gs == proto.gameOver:
                self.frozen = True
                self.gs_view.show_score()
            elif gs == proto.overTime:
                self.hud.update_prop(text='Overtime!')
        elif typ == proto.mapUpdate:
            ind, itemid, gt, spawn = data
            self.gs_view.set_time(gt)
            if ind == self.player.id:
                if isinstance(self.map.items[itemid], Triangle):
                    st = self.map.items[itemid].keystr
                    if not st in self.player.weapons.weapons:
                        self.player.weapons.pickup(st)
                    else:
                        if not isinstance(self.map.items[itemid], Ammo):
                            self.player.weapons.apply(st, self.player)
                        else:
                            self.player.weapons.predict_ammo(st)
            elif ind in self.players:
                if isinstance(self.map.items[itemid], Triangle):
                    st = self.map.items[itemid].keystr
                    if not st in self.players[ind].weapons.weapons:
                        self.players[ind].weapons.pickup(st)
                    else:
                        if not isinstance(self.map.items[itemid], Ammo):
                            try:
                                pl = self.players[ind]
                                pl.weapons.apply(st, pl)
                            except TypeError:
                                pass
                        else:
                            self.players[ind].weapons.predict_ammo(st)
            self.map.serverupdate(itemid, spawn)
        elif typ == proto.chat:
            ind, msg = data
            if ind == self.player.id:
                name = self.player.name
                color = self.player.color
            elif ind in self.players:
                name = self.players[ind].name
                color = self.players[ind].color
            else:
                name = self.specs[ind].name
                color = self.specs[ind].color
            #chatdata = ' '.join((name + ':', '\t', msg))
            chatdata = (name, color, msg)
            self.hud.update_prop(chat=chatdata)

    def send_to_client(self, dt):
        temp_input = proto.Input()
        self.time += int(dt * 1000000.)
        temp_input.CopyFrom(self.player.input)
        c_move = move(self.time, temp_input, self.player.state.copy())
        try:
            self.moves[self.index[0]] = c_move
        except IndexError:
            self.moves.append(c_move)
        self.moves.advance(self.index)
        self.send_message('input', (self.player.input, self.time))

    def spec_send(self, dt):
        self.time += int(dt * 1000000.)
        self.send_message('input', (proto.Input(), self.time))

    def draw(self):
        self.render.draw()

    def on_connect(self, msg):
        ind, mapname, name, gs = msg
        self.player.get_id(ind, name)
        batch = pyglet.graphics.Batch()
        self.map = Map(mapname, batch=batch, renderhook=self.render.maphook)
        self.render.maphook(self.map, add=True)
        print 'connected with id: ' + str(self.player.id)
        #self.send_message('input', (self.player.input, 1337))
        self.gs_view.init_self(ind, gs)
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

    def ready_up(self):
        msg = proto.Message()
        msg.type = proto.stateUpdate
        plr = proto.Player()
        plr.id = self.player.id
        msg.player.CopyFrom(plr)
        msg.gameState = proto.isReady
        self.send_message('other', msg)

    def send_chat(self, chatmsg):
        msg = proto.Message()
        msg.type = proto.chat
        plr = proto.Player()
        plr.id = self.player.id
        plr.chat = chatmsg
        msg.player.CopyFrom(plr)
        self.send_message('other', msg)

    def on_update(self, dt):
        pass

    def on_draw(self):
        pass

    def idle_update(self, dt):
        self.send_to_client(dt)
        self.gs_view.update(dt)
        self.proj_viewer.update(dt)
        self.hud.update(dt)

    def trans_to_spec(self):
        self.on_update = self.spec_update
        self.isSpec = 0.5
        self.player.state.hook_hud(self.hud.update_prop)
        self.hud.init_spec()
        self.gs_view.scorehook(self.gs_view.a.score, self.gs_view.b.score)
        self.player.remove_from_view()
        self.cross.remove()
        self.ready_cycle = False
        self.set_playergen()
        self.window.set_mouse_visible(True)
        self.window.set_exclusive_mouse(False)

    def trans_to_game(self):
        self.player.add_to_view()
        self.isSpec = False
        self.player.weapons.hook_hud(self.hud.update_prop)
        #self.player.state.hook_hud(self.hud.update_prop)
        self.hud.init_player(self.players)
        self.gs_view.add_self(self.player)
        self.cross.add(self.render.static_batch)
        self.on_update = self.game_update
        self.register_mouse()
        self.window.set_mouse_visible(False)
        self.window.set_exclusive_mouse(True)
        self.cancel_drag()

    def game_update(self, dt):
        self.rest_time += dt
        while self.rest_time >= timestep:
            if not self.frozen:
                self.update_physics(timestep)
            self.send_to_client(timestep)
            self.rest_time -= timestep

        #interpolate missing time
        state = self.player.state.copy()
        state = self.player.predict_step(self.rest_time, self.get_rect(),
                                         state, self.player.input)
        state.id = self.player.id
        state.color = self.player.color
        self.render.playerhook(state, update=True)

        self.camera.update(dt, self.player.state)
        self.proj_viewer.update(dt)
        self.gs_view.update(dt)
        self.hud.update(dt)
        self.cross.update(*self.camera.mpos)

    def spec_update(self, dt):
        if self.player.input.att and self.ready_cycle:
            try:
                self.ready_cycle = False
                if self.isSpec > 0.5:
                    self.players[self.isSpec].state.unhook()
                    self.players[self.isSpec].weapons.unhook()
                self.isSpec = self.playergen.next()
                id = self.isSpec
                self.players[id].state.hook_hud(self.hud.update_prop)
                self.players[id].weapons.hook_hud(self.hud.update_prop)
                self.unregister_mouse()
                self.cross.add(self.render.static_batch)
                self.hud.init_pers_hud()
                self.cancel_drag()
            except StopIteration:
                self.cancel_follow()
        if not self.player.input.att:
            self.ready_cycle = True
        if self.isSpec > 0.5:
            self.camera.update(dt, self.players[self.isSpec].state)
            self.cross.update(*self.camera.interpolate_mpos())
        else:
            self.player.specupdate(dt)
            self.camera.update(dt, self.player.state)
        self.spec_send(dt)
        self.proj_viewer.update(dt)
        self.gs_view.update(dt)
        self.hud.update(dt)

    def send_center(self, ind):
        if ind == self.player.id:
            pl = self.player
            return pl.rect.center, (pl.input.mx, pl.input.my)
        else:
            pl = self.players[ind]
            return pl.rect.center, (pl.input.mx, pl.input.my)

    def register_mouse(self):
            self.input_handler.register(self.camera.receive_m_pos, 'mouse_cam')
            self.window.set_mouse_visible(True)
            self.window.set_exclusive_mouse(False)

    def unregister_mouse(self):
        try:
            self.input_handler.unregister(self.camera.receive_m_pos)
            self.window.set_mouse_visible(False)
            self.window.set_exclusive_mouse(True)
        except KeyError:
            pass

    def set_playergen(self):
        self.playergen = iter(self.players.keys())

    def cancel_follow(self):
        ind = self.isSpec
        if ind > 0.5:
            self.player.state.pos = vec2(*self.players[ind].state.pos)
        self.isSpec = 0.5
        self.set_playergen()
        self.register_mouse()
        self.cross.remove()
        self.hud.init_spec()

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, mods):
            if buttons == 4:
                self.player.state.pos -= vec2(dx, dy) * 2

        self.dragevent = on_mouse_drag

    def cancel_drag(self):
        try:
            self.window.remove_handler('on_mouse_drag', self.dragevent)
        except AttributeError:
            pass

    def get_rect(self):
        playerlist = [player.rect for player in self.players.itervalues()
                      if not player.state.isDead]
        maplist = [rect for rect in self.map.quad_tree.retrieve([],
                   self.player.rect)]
        return playerlist + maplist
