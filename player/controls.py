from pyglet.window import key
from pyglet.event import EVENT_HANDLED
from network_utils import protocol_pb2 as proto
from options import Options


class InputHandler(object):
    """docstring for InputHandler"""
    def __init__(self, window):
        super(InputHandler, self).__init__()
        # list of pressed keys
        self.keys = key.KeyStateHandler()
        #keys are recognized as ints, this is an arbitrary offset to have
        # mouse clicks in the same dict
        self.mouse_offset = 1337
        self.window = window
        self.mousepos = [1280 / 2, 720 / 2]
        self.m_cam = [1280 / 2, 720 / 2]
        self.directns = proto.Input()
        self.listeners = {}
        # such keys as escape, ^
        self.controls = {}
        self.width = window.width
        self.height = window.height
        self.keys[key.ESCAPE] = False
        self.load_options()

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            self.mousepos[0] = x
            self.mousepos[1] = y
            self.m_cam[0] += dx
            self.m_cam[1] += dy
            self.m_cam[0] = 0 if self.m_cam[0] < 0 else self.width if (
                self.m_cam[0] > self.width) else self.m_cam[0]
            self.m_cam[1] = 0 if self.m_cam[1] < 0 else self.height if (
                self.m_cam[1] > self.height) else self.m_cam[1]
            self.send_message('changed_mouse', self.mousepos)
            self.send_message('mouse_cam', self.m_cam)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = True

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            self.keys[buttons + self.mouse_offset] = True
            self.mousepos[0] = x
            self.mousepos[1] = y
            self.m_cam[0] += dx
            self.m_cam[1] += dy
            self.send_message('changed_mouse', self.mousepos)
            self.send_message('mouse_cam', self.m_cam)

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = False

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                return EVENT_HANDLED

    def load_options(self):
        #realkeydict
        self.rkd = {}
        options = Options()
        for dkey, rkey in options.iteritems():
            try:
                self.rkd[dkey] = key.__getattribute__(rkey)
            except AttributeError:
                if rkey == 'M1':
                    self.rkd[dkey] = 1 + self.mouse_offset

    def process_keys(self, dt):
       # register pressed keys for movement
        try:
            self.directns.up = self.keys[self.rkd['up']]
            self.directns.left = self.keys[self.rkd['left']]
            self.directns.right = self.keys[self.rkd['right']]
            self.directns.down = self.keys[key.S]
            self.directns.att = self.keys[self.rkd['att']]
            if self.keys[self.rkd['blaster']]:
                self.directns.switch = proto.blaster
            elif self.keys[self.rkd['lg']]:
                self.directns.switch = proto.lg
            elif self.keys[self.rkd['sg']]:
                self.directns.switch = proto.sg
            elif self.keys[self.rkd['melee']]:
                self.directns.switch = proto.melee
            elif self.keys[self.rkd['gl']]:
                self.directns.switch = proto.gl
            else:
                self.directns.switch = proto.no_switch
            self.controls['esc'] = self.keys[key.ESCAPE]
            self.controls['f10'] = self.keys[key.F10]
            self.controls['rdy'] = self.keys[self.rkd['rdy']]
            self.controls['chat'] = self.keys[self.rkd['chat']]
        except KeyError:
            pass

        self.send_message('all_input', self.keys)

    def on_resize(self, width, height):
        self.width = width
        self.height = height

    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg):
        for listener, events in self.listeners.items():
            if event in events:
                try:
                    listener(event, msg)
                except (Exception, ):
                    self.unregister(listener, msg)

    def unregister(self, listener, msg=None):
        #print '%s deleted, %s' % (listener, msg)
        del self.listeners[listener]

    def receive_aim(self, event, msg):
        self.directns.mx, self.directns.my = msg[0], msg[1]
