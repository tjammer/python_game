import protocol_pb2 as proto


class AckManager(object):
    """docstring for AckManager"""
    def __init__(self):
        super(AckManager, self).__init__()
        self.acks = {}
        self.ack = 0

    def receive_send(self, func):
        self.send = func

    def send_rel(self, msg, address):
        self.ack += 1
        msg.ack = self.ack
        msg_string = msg.SerializeToString()
        self.send(msg_string, address)
        self.acks[self.ack] = [msg_string, address, 0, 0]

    def update(self, dt):
        for data in self.acks.itervalues():
            data[2] += dt
            if data[2] > .5:
                msg, address, time, count = data
                self.send(msg, address)
                data[2] = 0
                data[3] += 1
        for key, data in self.acks.items():
            if data[3] > 5:
                print 'del ack %i' % key
                del self.acks[key]

    def receive_ack(self, data):
        ack = data.ack
        if ack in self.acks:
            del self.acks[ack]

    def respond(self, msg, address):
        newmsg = proto.Message()
        newmsg.type = proto.ackResponse
        newmsg.ack = msg.ack
        self.send(newmsg.SerializeToString(), address)
        print 'send response %i' % msg.ack
