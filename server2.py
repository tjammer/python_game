from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from network_utils import serverclass
from time import time

t = [time()]
main = serverclass.GameServer()


def update(t):
    time_ = time()
    dt = time_ - t[0]
    main.update(dt)
    t[0] += time_

lc = LoopingCall(update, t)
reactor.listenUDP(8000, main)
reactor.run()
