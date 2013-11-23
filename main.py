import pyglet
from graphics import Camera
from player import controls, player

# set up window
window = pyglet.window.Window(1280, 720, vsync=False)
window.set_mouse_visible(False)
InputHandler = controls.Input_handler(window)
window.push_handlers(InputHandler.keys)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
Camera = Camera.Camera(window)
pyglet.clock.set_fps_limit(120)
Player = player.player()
# register movement with input
InputHandler.register(Player.Move.receive_message, events='get_input')


def update(dt):
    InputHandler.process_keys()
    Camera.get_mouse_pos(InputHandler.mousepos)
    Player.update(dt)
pyglet.clock.schedule(update)


@window.event
#draw
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(1, .9, .4, 1)
    Camera.set_camera()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.clock.tick()
    # draw Player
    Player.draw()
    Camera.set_static()
    fps.draw()

pyglet.app.run()
