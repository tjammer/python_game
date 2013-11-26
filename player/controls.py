from pyglet.window import key


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
        self.movement_input = {}
        self.listeners = {}

        @self.window.event
        def on_mouse_motion(x, y, dx, dy):
            # self.mousepos = [x, y]
            self.mousepos[0] += dx
            self.mousepos[1] += dy
            self.send_message('changed_mouse', self.mousepos)

        @self.window.event
        def on_mouse_press(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = True

        @self.window.event
        def on_mouse_release(x, y, button, modifiers):
            self.keys[button + self.mouse_offset] = False

    def process_keys(self):
       # register pressed keys for movement
        self.movement_input['up'] = self.keys[key.SPACE]
        self.movement_input['left'] = self.keys[key.A]
        self.movement_input['right'] = self.keys[key.D]
        self.send_message('movement_input', self.movement_input)
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
