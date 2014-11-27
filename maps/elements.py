from collision.caabb import cAABB as AABB


class Teleporter(AABB):
    """docstring for Teleporter"""
    def __init__(self, x, y, width, height, color, destination,
                 dest_sign, ind):
        super(Teleporter, self).__init__(x, y, width, height, color)
        self.destination = destination
        self.dest_sign = dest_sign
        self.ind = ind
        self.inactive = False

    def apply(self, player):
        player.state.pos = self.destination
        ##player.state.vel.y += 500
        player.state.set_cond('hold')
        if not player.move.sign_of(player.state.vel.x) == self.dest_sign:
            player.state.vel.x *= -1
        return False
