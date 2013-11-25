import pyglet
from graphics import camera
from menu.window_manager import WindowManager

# set up window
window = pyglet.window.Window(1280, 720, vsync=False)
window.set_mouse_visible(False)
WindowManager = WindowManager(window)
# load and init different modules
fps = pyglet.clock.ClockDisplay()
Camera = camera.Camera(window)
pyglet.clock.set_fps_limit(120)
# Player.register(Camera.receive_player_pos, events='changed_pos')


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
    Camera.set_static()
    WindowManager.draw()
    WindowManager.InputHandler.draw_mouse()
    fps.draw()

pyglet.app.run()
