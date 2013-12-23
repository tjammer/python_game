from twisted.internet.protocol import DatagramProtocol
import protocol_pb2 as proto


class GameServer(DatagramProtocol):
    """docstring for GameServer"""
    def __init__(self):
        super(GameServer, self).__init__()
        self.players = {}

