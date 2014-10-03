from twisted.internet import selectreactor
selectreactor.install()
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
    t[0] = time_

lc = LoopingCall(update, t)
lc.start(1 / 60.)
reactor.listenUDP(8000, main)
main.projectiles.receive_send(main.transport.write)
main.ackman.receive_send(main.transport.write)
reactor.run()
