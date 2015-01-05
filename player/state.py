from network_utils import protocol_pb2 as proto
from cvec2 import cvec2 as vec2


class state(object):
    """docstring for state"""
    def __init__(self, pos, vel, hp=100, armor=0, conds=False, isDead=False):
        super(state, self).__init__()
        self.pos, self.vel, self.hp, self.armor = pos, vel, hp, armor
        self.wall_t = .2
        self.wall = 0
        self.isDead = isDead
        self.frozen = False
        if not conds:
            self.conds = proto.MState()
            self.conds.canJump = True
        else:
            self.conds = conds
        self.hudhook = False
        self.chksm = hp + armor

    def set_cond(self, condname):
        if condname == 'ascending':
            self.conds.ascending = True
            self.conds.onGround = False
            self.conds.landing = False
            self.conds.canJump = False
            self.conds.onRightWall = False
            self.conds.onLeftWall = False
            self.conds.descending = False
        elif condname == 'canJump':
            self.conds.canJump = True
        elif condname == 'onGround':
            if not self.conds.onGround:
                if not self.conds.landing:
                    self.conds.landing = True
                    self.conds.descending = False
                    self.conds.ascending = False
                else:
                    self.conds.onGround = True
                    self.conds.landing = False
        elif condname == 'descending':
            self.conds.ascending = False
            self.conds.descending = True
            self.conds.onGround = False
            self.conds.landing = False
        elif condname == 'onRightWall':
            if not self.conds.onRightWall:
                self.conds.canJump = False
            self.conds.onRightWall = True
            self.conds.ascending = False
            self.conds.descending = False
            self.wall = self.wall_t
        elif condname == 'onLeftWall':
            if not self.conds.onLeftWall:
                self.conds.canJump = False
            self.conds.onLeftWall = True
            self.conds.ascending = False
            self.conds.descending = False
            self.wall = self.wall_t
        elif condname == 'hold':
            self.conds.hold = True

    def update(self, dt, stat):
        self.wall -= dt
        if self.wall < 0:
            self.wall = 0
            self.conds.onRightWall = False
            self.conds.onLeftWall = False
        if not stat.pos == self.pos:
            self.pos = vec2(*stat.pos)
        if not stat.vel == self.vel:
            self.vel = vec2(*stat.vel)
        self.hp = stat.hp
        self.armor = stat.armor
        if self.hudhook:
            self.hudhook(hp=str(self.hp), armor=str(self.armor))
        self.chksm = self.hp + self.armor
        self.conds.hold = stat.conds.hold

    def update_hp(self, stat):
        self.hp = stat.hp
        self.armor = stat.armor
        if self.hudhook:
            self.hudhook(hp=str(self.hp), armor=str(self.armor))
        self.chksm = self.hp + self.armor

    def copy(self):
        conds = proto.MState()
        conds.CopyFrom(self.conds)
        return state(vec2(*self.pos), vec2(*self.vel), self.hp, self.armor,
                     conds, self.isDead)

    def hook_hud(self, hudhook):
        self.hudhook = hudhook

    def unhook(self):
        if self.hudhook:
            self.hudhook = None
