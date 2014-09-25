from graphics.primitives import Rect


class DrawableArmor(Rect):
    """docstring for DrawableArmor"""
    def __init__(self, value, bonus, respawn, ind, *args, **kwargs):
        super(DrawableArmor, self).__init__(*args, **kwargs)
        self.inactive = False
        self.value = value
        self.bonus = bonus
        self.respawn = respawn
        self.ind = ind


class DrawableHealth(Rect):
    """docstring for DrawableHealth"""
    def __init__(self, *args, **kwargs):
        super(DrawableHealth, self).__init__(*args, **kwargs)
        self.inactive = False
