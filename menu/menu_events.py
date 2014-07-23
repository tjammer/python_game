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
        for listener, events in self.listeners.iteritems():
            try:
                listener(event, msg)
            except (Exception, ):
                self.unregister(listener, msg)

    def unregister(self, listener, msg):
        print '%s deleted, %s' % (listener, msg)
        del self.listeners[listener]


class MenuClass(object):
    """docstring for MenuClass
    base class for other menus to inherit from"""
    def __init__(self, vool=False):
        super(MenuClass, self).__init__()
        self.buttons = {}
        self.text_boxes = {}
        self.m_pos = [0, 0]
        self.keys = {}
        self.keys_old = {}
        self.listeners = {}
        self.bool = vool

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
        self.animate(dt)
        self.add_update(dt)

        for key, value in self.keys.items():
            self.keys_old[key] = value

    def draw(self):
        for key, panel in self.buttons.items() + self.text_boxes.items():
            panel.draw()

    def handle_clicks(self, key):
        pass

    def add_update(self, dt):
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
            #try:
            listener(event, msg)
            #except (Exception, ):
            #    self.unregister(listener)

    def unregister(self, listener):
        print '%s deleted' % listener
        del self.listeners[listener]

    # animation
    def animate(self, dt):
        for key, panel in self.buttons.items() + self.text_boxes.items():
            panel.pos[0] -= (panel.pos[0] - panel.target_pos[0])*dt * 0.15*30
            panel.update()
