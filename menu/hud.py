from pyglet.text import Label
from pyglet.text.document import FormattedDocument
from pyglet.text.layout import ScrollableTextLayout, IncrementalTextLayout
from network_utils import protocol_pb2 as proto
from pyglet.graphics import Batch
from gameplay.weapons import weaponcolors, allstrings
from graphics.primitives import font, Triangle


class Hud(object):
    """docstring for Hud"""
    def __init__(self, batch):
        super(Hud, self).__init__()
        self.text_ = 'This is the warmup phase'
        self.hp_t = '0'
        self.armor_t = '0'
        self.text_active = 5
        self.killmsg_active = False
        self.chat_active = False
        self.batch = batch
        self.hp = Label(self.hp_t, font_name=font, font_size=36,
                        bold=True, x=80, y=10, anchor_x='center',
                        anchor_y='bottom',
                        batch=self.batch)
        self.armor = Label(self.armor_t, font_name=font, font_size=36,
                           x=240, y=10, anchor_x='center', anchor_y='bottom',
                           bold=True,
                           batch=self.batch)
        self.text = Label(self.text_, font_name=font, font_size=36,
                          x=640, y=360, anchor_x='center', anchor_y='center',
                          batch=self.batch)
        self.weapon = Label('melee', font_name=font, font_size=32,
                            x=1160, y=80, anchor_x='center', anchor_y='bottom',
                            color=(0, 255, 255, 255),
                            batch=self.batch)
        self.ammo = Label('1', font_name=font, font_size=36,
                          x=1160, y=10, anchor_x='center', anchor_y='bottom',
                          bold=True,
                          batch=self.batch)
        self.time = Label('0:00', font_name=font, font_size=36,
                          x=640, y=680, anchor_x='center', anchor_y='center',
                          bold=True,
                          batch=self.batch)
        self.chatdoc = FormattedDocument('\n' * 11)
        #self.chatlog = document .FormattedDocument('\n')
        self.chat = ScrollableTextLayout(self.chatdoc, width=500,
                                         height=208, multiline=True,
                                         batch=self.batch)
        self.chat.x = 130
        self.chat.y = 130
        self.chat.content_valign = 'bottom'

        self.killdoc = FormattedDocument('\n')
        self.killmsg = ScrollableTextLayout(self.killdoc, width=300,
                                            height=104, multiline=True,
                                            batch=self.batch)
        self.killmsg.x = 20
        self.killmsg.y = 600

        self.scoredoc = FormattedDocument('0 : 0')
        self.score = ScrollableTextLayout(self.scoredoc, width=150,
                                          height=104, multiline=True,
                                          batch=self.batch)
        self.score.x = 1270
        self.score.y = 650
        self.score.anchor_x = 'right'
        self.score.anchor_y = 'center'

        self.normal_hpcol = (255, 255, 255, 255)
        self.low_hpcol = (255, 128, 0, 255)
        self.high_hpcol = (0, 204, 255, 255)
        self.bname = '_'
        self.aname = '_'
        self.gametime = 70
        self.weaponcolors = {proto.melee: (0, 255, 255, 255),
                             proto.explBlaster: (255, 255, 0, 255)}
        self.killmsg_count = 0
        self.scoreboard = None
        self.weaponbar = WeaponBar(self.batch)

    def init_player(self, players):
        if len(players) == 0:
            self.set_score(0, 0)
        else:
            self.bname = players.values()[0].name
            self.set_score(0, 0)
        self.weaponbar.batch = self.batch
        self.weapon.batch = self.batch
        self.ammo.batch = self.batch
        self.hp.batch = self.batch
        self.armor.begin_update()
        self.armor.batch = self.batch
        self.armor.end_update()

    def init_spec(self):
        self.weaponbar.remove()
        self.weapon.delete()
        self.ammo.delete()
        self.hp.delete()
        self.armor.delete()

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
            if armor != self.armor.text:
                self.armor.text = armor
                if int(armor) <= 20:
                    self.armor.color = self.low_hpcol
                elif int(armor) > 100:
                    self.armor.color = self.high_hpcol
                else:
                    self.armor.color = self.normal_hpcol
        if hp:
            if hp != self.hp.text:
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
            self.text.batch = self.batch
            self.text.end_update()
        if weapon:
            if weapon != self.weapon.text:
                self.weapon.text = weapon
                wkey = [key for key, val in allstrings.iteritems()
                        if val == weapon][0]
                self.weapon.color = weaponcolors[wkey] + [255]
        if ammo:
            ammo, weapons = ammo
            if ammo != self.ammo.text:
                self.ammo.text = ammo
            self.weaponbar.update(weapons)
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
            self.chat.batch = self.batch()
            self.chat.view_y = -self.chat.content_height
            self.chat.end_update()
            self.chat_active = 4

    def set_score(self, a, b, msg=False, scoreboard=False):
        self.score.begin_update()
        self.scoredoc.delete_text(0, len(self.scoredoc.text))
        self.scoredoc.insert_text(0, ''.join((str(a), '   ', self.aname, '\n',
                                              str(b), '   ', self.bname)),
                                  dict(color=[255] * 4))
        apos = self.scoredoc.get_paragraph_start(1)
        bpos = self.scoredoc.get_paragraph_start(len(self.scoredoc.text) - 1)
        self.scoredoc.set_style(apos, apos+len(str(a)), dict(font_size=24,
                                baseline=-6))
        self.scoredoc.set_style(bpos, bpos+len(str(b)), dict(font_size=24,
                                baseline=-6))
        self.score.end_update()
        self.score.width = self.score.content_width + 40
        if msg:
            w, killer, killed = msg
            if w == 11:
                w = 4
            if w == 12:
                w = 5
            wcol = weaponcolors['w' + str(w-1)]
            self.killmsg.begin_update()
            self.killdoc.insert_text(len(self.killdoc.text), killer,
                                     dict(color=[255] * 4))
            self.killdoc.insert_text(len(self.killdoc.text), ' fragged',
                                     dict(color=wcol + [255]))
            self.killdoc.insert_text(len(self.killdoc.text), ' '.join(('',
                                     killed, '\n')),
                                     dict(color=[255] * 4))
            self.killmsg.batch = self.batch
            if not self.killmsg_active:
                self.killmsg_active = 4
            self.killmsg_count += 1
            self.killmsg.end_update()
        if scoreboard:
            self.scoreboard = ScoreBoard((a, self.aname), (b, self.bname),
                                         self.batch)
        else:
            if not self.scoreboard is None:
                self.scoreboard.delete()
                self.scoreboard = None

    def calc_time(self, gametime):
        mins = '{:01.0f}'.format(gametime // 60)
        secs = '{:02.0f}'.format(gametime % 60)
        return ''.join((mins, ':', secs))


class ScoreBoard(object):
    """docstring for ScoreBoard"""
    def __init__(self, a, b, batch):
        super(ScoreBoard, self).__init__()
        self.ascore, self.aname = a
        self.bscore, self.bname = b
        self.adoc = FormattedDocument('\t'.join((self.aname,
                                      str(self.ascore))))
        self.bdoc = FormattedDocument('\t'.join((str(self.bscore),
                                      self.bname)))
        scsize = 100
        nmsize = 32

        self.alayout = ScrollableTextLayout(self.adoc, width=400, height=300,
                                            batch=batch, multiline=True)
        w = 400 - len(str(self.ascore)) * scsize * 72 / 96
        self.adoc.set_style(0, len(self.adoc.text), dict(wrap=False,
                            color=[255]*4, align='left', tab_stops=[w]))
        self.adoc.set_style(0, len(self.aname), dict(font_size=nmsize))
        a = len(self.aname)+1
        self.adoc.set_style(a, a + len(str(self.ascore)),
                            dict(font_size=scsize, baseline=-scsize / 4))

        self.alayout.x = 1280 / 2
        self.alayout.y = 720 / 2 + 50
        self.alayout.anchor_x = 'right'
        self.alayout.anchor_y = 'center'

        self.blayout = ScrollableTextLayout(self.bdoc, width=400, height=300,
                                            batch=batch, multiline=True)
        w = 400 - len(str(self.bname)) * nmsize * 72 / 96
        self.bdoc.set_style(0, len(self.bdoc.text), dict(wrap=False,
                            color=[255]*4, align='right', tab_stops=[w]))
        self.bdoc.set_style(0, len(str(self.bscore)), dict(font_size=scsize,
                            baseline=-scsize / 4))
        a = len(str(self.bscore))+1
        self.bdoc.set_style(a, a + len(self.bname), dict(font_size=nmsize))

        self.blayout.x = 1280 / 2
        self.blayout.y = 720 / 2 + 50
        self.blayout.anchor_x = 'left'
        self.blayout.anchor_y = 'center'

    def delete(self):
        self.alayout.delete()
        self.blayout.delete()


class WeaponBar(object):
    """docstring for WeaponBar"""
    def __init__(self, batch):
        super(WeaponBar, self).__init__()
        self.batch = batch
        self.weapons = {'1': 1, '2': 1, '3': 1}
        self.ammos = []
        self.tris = []

    def __len__(self):
        return len(self.weapons)

    def init_bar(self, weapons):
        try:
            self.ammolayout.delete()
            for tri in self.tris:
                tri.remove()
        except AttributeError:
            pass
        ammotext = '\t'.join(str(w.ammo) for key, w in weapons.iteritems()
                             if key != 'w0')
        self.ammos = ammotext.split('\t')
        self.ammodoc = FormattedDocument(ammotext)
        self.ammodoc.set_style(0, len(ammotext), dict(color=[255]*4,
                               tab_stops=[120*(i+1) for i in range(6)],
                               font_size=24, align='center', wrap=False))
        self.ammolayout = IncrementalTextLayout(self.ammodoc, width=600,
                                                height=50, batch=self.batch,
                                                multiline=True)
        self.ammolayout.x = 1280 / 2
        self.ammolayout.y = 20
        self.ammolayout.anchor_x = 'center'
        self.ammolayout.anchor_y = 'bottom'
        w = self.ammolayout.content_width
        colorlist = [weaponcolors[key] for key in weapons if key != 'w0']
        self.tris = [Triangle(640-w/2-52+120*i, 35, 50, 50, col,
                     self.batch, 0, 0) for i, col in enumerate(colorlist)]

    def update(self, weapons):
        if len(weapons) != len(self.weapons):
            self.init_bar(weapons)
            self.weapons = weapons.copy()
        else:
            ammotext = '\t'.join(str(w.ammo) for key, w in weapons.iteritems()
                                 if key != 'w0')
            ammos = ammotext.split('\t')
            self.ammolayout.begin_update()
            for i, a in enumerate(ammos):
                if a != self.ammos[i]:
                    ln = sum(len(self.ammos[j]) for j in range(i)) + i
                    self.ammodoc.delete_text(ln, ln + len(self.ammos[i]))
                    self.ammodoc.insert_text(ln, a)
            self.ammolayout.end_update()

            self.ammos = ammos

    def remove(self):
        try:
            self.ammolayout.delete()
            for tri in self.tris:
                tri.remove()
        except AttributeError:
            pass
