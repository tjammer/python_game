import pygletreactor
pygletreactor.install()
from twisted.internet import reactor, task
from network_utils import serverclass

main = serverclass.GameServer()
# send updates to every connected player 60 times per second
t = task.LoopingCall(main.send_all)
t.start(1 / 60.)

reactor.listenUDP(8000, main)
reactor.run()
