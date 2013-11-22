import pyglet
from graphics import primitives, Camera
from player import controls, movement

# set up window
window = pyglet.window.Window(800, 450, vsync=True)
window.set_mouse_visible(False)
InputHandler = controls.Input_handler(window)
window.push_handlers(InputHandler.keys)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
Camera = Camera.Camera(window)
pyglet.clock.set_fps_limit(120)
Rect = primitives.Rect(0, 0, window.width / 40, window.height / 10, (0, .8, 1))
Move = movement.Move()
# register movement with input
InputHandler.register(Move.receive_message, events='get_input')


def update(dt):
    InputHandler.process_keys()
    Camera.get_mouse_pos(InputHandler.mousepos)
    Move.update(dt)
    Rect.update(Move.pos[0], Move.pos[1])
pyglet.clock.schedule(update)


@window.event
#draw
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(1, .9, .4, 1)
    Camera.set_camera()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    # draw Rect
    Rect.draw()
    Camera.set_static()
    fps.draw()

pyglet.app.run()
