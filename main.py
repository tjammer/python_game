import pyglet
import pygletreactor
pygletreactor.install()
from twisted.internet import reactor
from menu.window_manager import WindowManager
from network_utils.clientclass import Client

window = pyglet.window.Window(1280, 720, vsync=False)
#window.set_mouse_visible(True)
window.set_exclusive_mouse(True)
window_manager = WindowManager(window)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
fps_limit = 120.
#pyglet.clock.set_fps_limit(fps_limit)
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
    #pyglet.gl.glClearColor(0, .0, 0, 1)
    #pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    window_manager.draw()
    fps.draw()

reactor.listenUDP(8001, client)
client.register_ack()
reactor.run(call_interval=1./fps_limit)
