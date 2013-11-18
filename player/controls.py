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
        self.movement_input = {}
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
       # register pressed keys for movement
        self.movement_input['up'] = self.keys[key.SPACE]
        self.movement_input['left'] = self.keys[key.A]
        self.movement_input['right'] = self.keys[key.D]
        self.send_message('get_input', self.movement_input)

    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg):
        for listener, events in self.listeners.items():
            if event in events:
                listener(event, msg)
