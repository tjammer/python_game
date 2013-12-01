from pyglet.window import key
from pyglet.event import EVENT_HANDLED


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
        self.directns = {}
        self.listeners = {}
        # such keys as escape, ^
        self.controls = {}

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            self.mousepos[0] += dx
            self.mousepos[1] += dy
            self.send_message('changed_mouse', self.mousepos)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = True

        @self.window.event
        def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
            self.keys[buttons + self.mouse_offset] = True
            self.mousepos[0] += dx
            self.mousepos[1] += dy
            self.send_message('changed_mouse', self.mousepos)

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = False

        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.ESCAPE:
                return EVENT_HANDLED

    def process_keys(self):
       # register pressed keys for movement
        self.directns['up'] = self.keys[key.SPACE]
        self.directns['left'] = self.keys[key.A]
        self.directns['right'] = self.keys[key.D]
        self.controls['esc'] = self.keys[key.ESCAPE]
        self.controls['f10'] = self.keys[key.F10]

        self.send_message('all_input', self.keys)

    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg):
        for listener, events in self.listeners.items():
            if event in events:
                try:
                    listener(event, msg)
                except (Exception, ):
                    self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]
