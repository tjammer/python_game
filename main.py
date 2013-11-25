import pyglet
from graphics import camera
from player import controls, player
from menu.elements import TextBoxFramed

# set up window
window = pyglet.window.Window(1280, 720, vsync=False)
window.set_mouse_visible(False)
InputHandler = controls.InputHandler(window)
window.push_handlers(InputHandler.keys)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
Camera = camera.Camera(window)
pyglet.clock.set_fps_limit(120)
Player = player.player()
# register movement with input, camera with playerpos
InputHandler.register(Player.Move.receive_message, events='get_input')
InputHandler.register(Camera.receive_mouse_pos, events='changed_mouse')
Player.register(Camera.receive_player_pos, events='changed_pos')
box = TextBoxFramed([500, 400], [300, 100], 2, 'start game')


def update(dt):
    InputHandler.process_keys()
    Player.update(dt)
    Camera.update(dt)
pyglet.clock.schedule(update)


@window.event
#draw
def on_draw():
    pyglet.clock.tick()
    window.clear()
    pyglet.gl.glClearColor(0, .0, 0, 1)
    Camera.set_camera()
    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    # draw Player
    Player.draw()
    Camera.set_static()
    box.draw()
    InputHandler.draw_mouse()
    fps.draw()

pyglet.app.run()
