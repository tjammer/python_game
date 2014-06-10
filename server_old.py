# import pyglet
import pygletreactor
pygletreactor.install()
from twisted.internet import reactor
from network_utils import serverclass

main = serverclass.GameServer()

pygletreactor.pyglet.clock.schedule_interval_soft(main.update, 1 / 60.)

reactor.listenUDP(8000, main)
reactor.run(call_interval=1 / 60.)
