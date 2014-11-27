import pyglet
import pygletreactor
pygletreactor.install()
from twisted.internet import reactor
from menu.window_manager import WindowManager
from network_utils.clientclass import Client
from graphics import get_window
from player.options import Options
import sys
sys.path.append('/home/jammer/Documents/render/')
from model import Model
from graphics.shader import Shader, vec3
from pyglet.gl import *
from graphics.vec3 import vec3 as cvec3

vert = """varying vec3 normal;
varying vec4 orig_color, vertex;

void main()
{
    normal = gl_Normal;
    gl_Position = ftransform();
    orig_color = gl_Color;
    vertex = gl_Vertex;

}"""

frag = """
uniform vec3 lightPos;
varying vec3 normal;
varying vec4 orig_color, vertex;

void main()
{
    float intensity, distance;
    vec4 color;
    vec3 vtx;
    vtx = vec3(vertex[0], vertex[1], vertex[2]);
    intensity = dot(normalize(lightPos),normalize(normal));
    distance = distance(lightPos, vtx);

    if (intensity > 0.95)
        color = orig_color * 2.;
    else if (intensity > 0.5)
        color = orig_color * 1.5;
    else
        color = orig_color * 1.;

    gl_FragColor = color;

}"""

shader = Shader(vertex=vert, fragment=frag)
#shader.set('lightDir', vec3(-50, 50., -50.))
lightpos = [0., 0., 0.]
rottrans = [0, 0, 1, 0, 0, 0, 0]


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

model = Model('/home/jammer/Documents/blenders/firstchar/colors.obj')
#mesh = Mesh(*load_obj_file('/home/jammer/Documents/blenders/thing.obj'))
batch = pyglet.graphics.Batch()
model.add(batch)


def update(dt):
    window_manager.update(dt)
    client.update(dt)
    model.move(rottrans)
pyglet.clock.schedule(update)


"""@window.event
def on_key_press(symbol, mod):
    if symbol == pyglet.window.key.UP:
        lightpos[2] += 10
    elif symbol == pyglet.window.key.DOWN:
        lightpos[2] -= 10
    elif symbol == pyglet.window.key.ENTER:
        print lightpos
    elif symbol == pyglet.window.key.RIGHT:
        rottrans[0] = 1
    elif symbol == pyglet.window.key.LEFT:
        rottrans[0] = -1"""

"""@window.event
def on_key_release(symbol, mod):
    rottrans[0] = 0

@window.event
def on_mouse_motion(x, y, dx, dy):
    lightpos[0] = (x - 1280. / 2)
    lightpos[1] = (y - 300)"""


@window.event
#draw
def on_draw():
    window.clear()
    pyglet.gl.glClearColor(.9, .9, .9, 1)
    window_manager.draw()
    fps.draw()
    try:
        with window_manager.current_screen.camera:
            shader.set('lightPos', vec3(*lightpos))
            #pyglet.gl.glEnable(pyglet.gl.GL_CULL_FACE)
            glEnable(GL_DEPTH_TEST)
            shader.push()
            batch.draw()
            shader.pop()
            glDisable(GL_DEPTH_TEST)
            glClearDepth(1)
            #pyglet.gl.glDisable(pyglet.gl.GL_CULL_FACE)
    except AttributeError:
        pass

reactor.listenUDP(59447, client)
client.register_ack()
reactor.run(call_interval=1./fps_limit)
