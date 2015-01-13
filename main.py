import pyglet
#pyglet.options['debug_gl'] = False
import pygletreactor
pygletreactor.install()
from twisted.internet import reactor
from menu.window_manager import WindowManager
from network_utils.clientclass import Client
from graphics import get_window
from player.options import Options

window = get_window(Options())
window.set_exclusive_mouse(True)
window_manager = WindowManager(window)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
fps_limit = 120.
client = Client()
window_manager.connect = client.start_connection
window_manager.disconnect = client.disconnect
window_manager.register(client.get_input, ('input', 'other'))
client.register(window_manager.receive_events, ('serverdata', 'on_connect'))


def update(dt):
    window_manager.update(dt)
    client.update(dt)
pyglet.clock.schedule(update)


@window.event
#draw
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(.9, .9, .9, 1)
    window_manager.draw()
    fps.draw()

reactor.listenUDP(59447, client)
client.register_ack()
reactor.run(call_interval=1./fps_limit)
