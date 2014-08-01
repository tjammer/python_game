from pyglet.text import Label
from network_utils import protocol_pb2 as proto
from pyglet.graphics import Batch


class Hud(object):
    """docstring for Hud"""
    def __init__(self):
        super(Hud, self).__init__()
        self.text_ = 'This is the warmup phase'
        self.hp_t = '0'
        self.armor_t = '0'
        self.text_active = 5
        self.killmsg_active = False
        self.labellist = Batch()
        font = 'Helvetica'
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
        self.killmsg = Label('0:00', font_name=font, font_size=36,
                             x=640, y=680, anchor_x='left', anchor_y='center')
        self.score = Label('me 0:0 enemy', font_name=font, font_size=24,
                           x=1260, y=680, anchor_x='right', anchor_y='center',
                           batch=self.labellist)
        self.normal_hpcol = (255, 255, 255, 255)
        self.low_hpcol = (255, 128, 0, 255)
        self.high_hpcol = (0, 204, 255, 255)
        self.enemyname = '_'
        self.ownname = 'me'
        self.gametime = 70
        self.weaponcolors = {proto.melee: (0, 255, 255, 255),
                             proto.explBlaster: (255, 255, 0, 255)}

    def init_player(self, players):
        if len(players) == 0:
            self.enemyname = '_'
            self.set_score(0, 0)
        else:
            self.enemyname = players.values()[0].name
            self.set_score(0, 0)

    def draw(self):
        self.labellist.draw()

    def update(self, dt):
        if self.text_active:
            self.text_active -= dt
            if self.text_active <= 0:
                self.text_active = False
                self.text.delete()
        if self.killmsg_active:
            self.killmsg_active -= dt
            if self.killmsg_active <= 0:
                self.killmsg_active = False
                self.killmsg.delete()
        self.time.text = self.calc_time(self.gametime)

    def update_prop(self, armor=False, hp=False, text=False, weapon=False,
                    ammo=False, time=False, score=False, msg=False):
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
            self.text.text = text
            self.text_active = 2
            self.text.batch = self.labellist
        if weapon:
            self.weapon.text = weapon
            if weapon == 'melee':
                self.weapon.color = (0, 255, 255, 255)
            elif weapon == 'blaster':
                self.weapon.color = (255, 255, 0, 255)
        if ammo:
            self.ammo.text = ammo
        if isinstance(time, float):
            self.gametime = time
        if score:
            self.enemyname = score
            self.score.text = '0:0 ' + self.enemyname

    def set_score(self, own, other, msg=False):
        self.score.text = ' '.join((self.ownname,
                                   str(own), ':', str(other),
                                   self.enemyname))

    def calc_time(self, gametime):
        mins = '{:01.0f}'.format(gametime // 60)
        secs = '{:02.0f}'.format(gametime % 60)
        return ''.join((mins, ':', secs))
