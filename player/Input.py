from pyglet.window import key


class Input_handler(object):
    """docstring for Input_handler"""
    def __init__(self, window):
        super(Input_handler, self).__init__()
        # list of pressed keys
        self.keys = key.KeyStateHandler()
        #keys are recognized as ints, this is an arbitrary offset to have
        # mouse clicks in the same dict
        self.mouse_offset = 1337
        self.window = window
        self.mousepos = [0, 0]
        self.listeners = {}

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            self.mousepos = [x, y]

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = True

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = False

    def process_keys(self):
        if self.keys[key.A]:
            print self.keys

    def register(self, listener, events=None):
        self.listeners[listener] = events
        # asdf
