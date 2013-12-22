import pyglet
import pygletreactor
pygletreactor.install()
from twisted.internet import reactor
from menu.window_manager import WindowManager

# set up window
window = pyglet.window.Window(1280, 720, vsync=False)
# window.set_mouse_visible(True)
window.set_exclusive_mouse(True)
WindowManager = WindowManager(window)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
pyglet.clock.set_fps_limit(120)


def update(dt):
    WindowManager.update(dt)
pyglet.clock.schedule(update)


@window.event
#draw
def on_draw():
    pyglet.clock.tick()
    window.clear()
    pyglet.gl.glClearColor(0, .0, 0, 1)
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    WindowManager.draw()
    fps.draw()

reactor.run()
