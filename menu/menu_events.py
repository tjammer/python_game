class Events(object):
    """docstring for Events
    class for menu classes to inherit events"""
    def __init__(self):
        super(Events, self).__init__()
        self.listeners = {}

    # receive events
    def receive_event(self, event, msg):
        if event == 'changed_mouse':
            self.m_pos = msg
        if event == 'all_input':
            self.keys = msg

    # send events
    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg=None):
        for listener, events in self.listeners.items():
            try:
                listener(event, msg)
            except (Exception, ):
                self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]


class MenuClass(object):
    """docstring for MenuClass
    base class for other menus to inherit from"""
    def __init__(self):
        super(MenuClass, self).__init__()
        self.buttons = {}
        self.text_boxes = {}
        self.m_pos = [0, 0]
        self.keys = {}
        self.listeners = {}

    def update(self, dt):
        for key, button in self.buttons.items():
            if button.in_box(self.m_pos):
                button.Box.highlight()
                try:
                    if self.keys[1338]:
                        self.handle_clicks(key)
                except KeyError:
                    continue
            else:
                button.Box.restore()

    def draw(self):
        for key, button in self.buttons.items():
            button.draw()
        for key, box in self.text_boxes.items():
            box.draw()

    def handle_clicks(self, key):
        pass

    # receive events
    def receive_event(self, event, msg):
        if event == 'changed_mouse':
            self.m_pos = msg
        if event == 'all_input':
            self.keys = msg

    # send events
    def register(self, listener, events=None):
        self.listeners[listener] = events

    def send_message(self, event, msg=None):
        for listener, events in self.listeners.items():
            try:
                listener(event, msg)
            except (Exception, ):
                self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]
