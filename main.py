import pyglet
from graphics import Primitives, Camera
from player import Input

# set up window
window = pyglet.window.Window(800, 450, vsync=True)
window.set_mouse_visible(False)
input_handler = Input.Input_handler(window)
window.push_handlers(input_handler.keys)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
camera = Camera.Camera(window)
pyglet.clock.set_fps_limit(120)
rect = Primitives.Rect(0, 0, window.width / 40, window.height / 10, (0, .8, 1))


def update(dt):
    input_handler.process_keys()
    camera.get_mouse_pos(input_handler.mousepos)
pyglet.clock.schedule(update)


@window.event
#draw
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(1, .9, .4, 1)
    camera.set_camera()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    # draw rect
    rect.draw()
    camera.set_static()
    fps.draw()

pyglet.app.run()
