import protocol_pb2.py as proto


class Move(object):
    """docstring for Move"""
    def __init__(self, input, pos, vel):
        super(Move, self).__init__()
        self.input = input
        self.pos = pos
        self.vel = vel
