from pyglet.text import Label, document, layout
from network_utils import protocol_pb2 as proto
from pyglet.graphics import Batch
from gameplay.weapons import weaponcolors, allstrings
from graphics.primitives import font


class Hud(object):
    """docstring for Hud"""
    def __init__(self):
        super(Hud, self).__init__()
        self.text_ = 'This is the warmup phase'
        self.hp_t = '0'
        self.armor_t = '0'
        self.text_active = 5
        self.killmsg_active = False
        self.chat_active = False
        self.labellist = Batch()
        self.speclist = Batch()
        self.active_batch = self.speclist
        self.hp = Label(self.hp_t, font_name=font, font_size=36,
                        bold=True, x=80, y=10, anchor_x='center',
                        anchor_y='bottom',
                        batch=self.labellist)
        self.armor = Label(self.armor_t, font_name=font, font_size=36,
                           x=240, y=10, anchor_x='center', anchor_y='bottom',
                           bold=True,
                           batch=self.labellist)
        self.text = Label(self.text_, font_name=font, font_size=36,
                          x=640, y=360, anchor_x='center', anchor_y='center',
                          batch=self.labellist)
        self.weapon = Label('melee', font_name=font, font_size=32,
                            x=1160, y=80, anchor_x='center', anchor_y='bottom',
                            color=(0, 255, 255, 255),
                            batch=self.labellist)
        self.ammo = Label('1', font_name=font, font_size=36,
                          x=1160, y=10, anchor_x='center', anchor_y='bottom',
                          bold=True,
                          batch=self.labellist)
        self.time = Label('0:00', font_name=font, font_size=36,
                          x=640, y=680, anchor_x='center', anchor_y='center',
                          bold=True,
                          batch=self.labellist)
        self.score = Label('me 0:0 enemy', font_name=font, font_size=24,
                           x=1260, y=680, anchor_x='right', anchor_y='center',
                           batch=self.labellist)
        self.chatdoc = document.FormattedDocument('\n' * 11)
        #self.chatlog = document .FormattedDocument('\n')
        self.chat = layout.ScrollableTextLayout(self.chatdoc, width=500,
                                                height=208, multiline=True,
                                                batch=self.labellist)
        self.chat.x = 130
        self.chat.y = 130
        self.chat.content_valign = 'bottom'

        self.killdoc = document.FormattedDocument('\n')
        self.killmsg = layout.ScrollableTextLayout(self.killdoc, width=300,
                                                   height=104, multiline=True,
                                                   batch=self.labellist)
        self.killmsg.x = 20
        self.killmsg.y = 600

        self.normal_hpcol = (255, 255, 255, 255)
        self.low_hpcol = (255, 128, 0, 255)
        self.high_hpcol = (0, 204, 255, 255)
        self.bname = '_'
        self.aname = '_'
        self.gametime = 70
        self.weaponcolors = {proto.melee: (0, 255, 255, 255),
                             proto.explBlaster: (255, 255, 0, 255)}
        self.killmsg_count = 0

    def init_player(self, players):
        if len(players) == 0:
            self.set_score(0, 0)
        else:
            self.bname = players.values()[0].name
            self.set_score(0, 0)
        self.time.batch = self.labellist
        self.active_batch = self.labellist

    def init_spec(self):
        self.time.batch = self.speclist
        self.active_batch = self.speclist

    def draw(self):
        self.active_batch.draw()

    def update(self, dt):
        if self.text_active:
            self.text_active -= dt
            if self.text_active <= 0:
                self.text_active = False
                self.text.delete()
        if self.killmsg_active:
            self.killmsg_active -= dt
            if self.killmsg_active <= 0:
                self.killmsg_count -= 1
                start = self.killdoc.get_paragraph_start(1)
                end = self.killdoc.get_paragraph_end(1)
                self.killdoc.delete_text(start, end)
                if self.killmsg_count > 0:
                    self.killmsg_active = 4
                else:
                    self.killmsg_active = False
                    self.killmsg.delete()
        if self.chat_active:
            self.chat_active -= dt
            if self.chat_active <= 0:
                self.chat_active = False
                self.chat.delete()
        self.time.text = self.calc_time(self.gametime)

    def update_prop(self, armor=False, hp=False, text=False, weapon=False,
                    ammo=False, time=False, name=False, msg=False, chat=None):
        if armor:
            self.armor.text = armor
            if int(armor) <= 20:
                self.armor.color = self.low_hpcol
            elif int(armor) > 100:
                self.armor.color = self.high_hpcol
            else:
                self.armor.color = self.normal_hpcol
        if hp:
            self.hp.text = hp
            if int(hp) <= 20:
                self.hp.color = self.low_hpcol
            elif int(hp) > 100:
                self.hp.color = self.high_hpcol
            else:
                self.hp.color = self.normal_hpcol
        if text:
            self.text.begin_update()
            self.text.text = text
            self.text_active = 1
            self.text.batch = self.active_batch
            self.text.end_update()
        if weapon:
            self.weapon.text = weapon
            if weapon == allstrings['w0']:
                self.weapon.color = weaponcolors['w0'] + [255]
            if weapon == allstrings['w1']:
                self.weapon.color = weaponcolors['w1'] + [255]
            if weapon == allstrings['w2']:
                self.weapon.color = weaponcolors['w2'] + [255]
            if weapon == allstrings['w3']:
                self.weapon.color = weaponcolors['w3'] + [255]
        if ammo:
            self.ammo.text = ammo
        if isinstance(time, float):
            self.gametime = time
        if name:
            a, name = name
            if a:
                self.aname = name
            else:
                self.bname = name
            #self.score.text = '0:0 ' + self.bname
        if chat:
            name, color, msg = chat
            self.chat.begin_update()
            #self.chat.text = chat
            self.chatdoc.insert_text(len(self.chatdoc.text), name,
                                     dict(color=list(color) + [255],
                                          bold=True))
            self.chatdoc.insert_text(len(self.chatdoc.text), '\t' + msg + '\n',
                                     dict(color=[255] * 4, bold=False))
            start = self.chatdoc.get_paragraph_start(0)
            end = self.chatdoc.get_paragraph_end(0)
            self.chatdoc.delete_text(start, end)
            """self.chatlog.insert_text(len(self.chatlog.text), name,
                                     dict(color=list(color) + [255],
                                          bold=True))
            self.chatlog.insert_text(len(self.chatlog.text), '\t' + msg + '\n',
                                     dict(color=[255] * 4, bold=False))"""
            self.chat.batch = self.active_batch
            self.chat.view_y = -self.chat.content_height
            self.chat.end_update()
            self.chat_active = 4

    def set_score(self, a, b, msg=False):
        self.score.text = ' '.join((self.aname,
                                   str(a), ':', str(b),
                                   self.bname))
        if msg:
            w, killer, killed = msg
            if w == 11:
                w = 4
            wcol = weaponcolors['w' + str(w-1)]
            self.killmsg.begin_update()
            self.killdoc.insert_text(len(self.killdoc.text), killer,
                                     dict(color=[255] * 4))
            self.killdoc.insert_text(len(self.killdoc.text), ' killed',
                                     dict(color=wcol + [255]))
            self.killdoc.insert_text(len(self.killdoc.text), ' '.join(('',
                                     killed, '\n')),
                                     dict(color=[255] * 4))
            self.killmsg.batch = self.active_batch
            if not self.killmsg_active:
                self.killmsg_active = 4
            self.killmsg_count += 1
            self.killmsg.end_update()

    def calc_time(self, gametime):
        mins = '{:01.0f}'.format(gametime // 60)
        secs = '{:02.0f}'.format(gametime % 60)
        return ''.join((mins, ':', secs))
