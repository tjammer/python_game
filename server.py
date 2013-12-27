import pyglet
import pygletreactor
pygletreactor.install()
from twisted.internet import reactor
from network_utils import serverclass

main = serverclass.GameServer()

pyglet.clock.schedule_interval(main.update, 1 / 60.)

reactor.listenUDP(8000, main)
reactor.run()
