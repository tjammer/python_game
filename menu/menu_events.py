from player.state import vec2
try:
    from pyglet.graphics import Batch
    from pyglet.window import key as key_
    from elements import MenuLayout
except:
    pass


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
            #try:
            listener(event, msg)
            #except (Exception, ):
            #    self.unregister(listener, msg)

    def unregister(self, listener, msg):
        print '%s deleted, %s' % (listener, msg)
        del self.listeners[listener]


class MenuClass(object):
    """docstring for MenuClass
    base class for other menus to inherit from"""
    def __init__(self, vool=False, window=None):
        super(MenuClass, self).__init__()
        from pyglet.graphics import Batch
        from pyglet.window import key as key_
        self.buttons = {}
        #self.text_boxes = {}
        self.m_pos = [0, 0]
        self.keys = key_.KeyStateHandler()
        self.keys_old = key_.KeyStateHandler()
        self.listeners = {}
        self.bool = vool
        self.keys_old[key_.ESCAPE] = True
        self.batch = Batch()
        self.window = window
        self.scale = vec2(window.width / 1280., window.height / 720.)

        @window
        def on_resize(width, height):
            self.scale = vec2(width / 1280., height / 720.)

    def update(self, dt):
        for key, button in self.buttons.items():
            if button.in_box(self.m_pos):
                button.highlight()
                try:
                    if self.keys[1338]:
                        self.handle_clicks(key)
                except KeyError:
                    continue
            else:
                button.restore()
        #self.animate(dt)
        self.add_update(dt)

        self.keys_old.update(self.keys)
        #for key, value in self.keys.items():
        #    self.keys_old[key] = value

    def draw(self):
        self.batch.draw()

    def handle_clicks(self, key):
        pass

    def add_update(self, dt):
        pass

    def on_draw(self):
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
        for key, panel in self.buttons.items():
            panel.pos[0] -= (panel.pos[0] - panel.target_pos[0])*dt * 0.15*30
            panel.update()


class NewMenu(object):
    """docstring for NewMenu"""
    def __init__(self, vool=None, window=None):
        super(NewMenu, self).__init__()
        #self.text_boxes = {}
        self.m_pos = [0, 0]
        self.keys = key_.KeyStateHandler()
        self.keys_old = key_.KeyStateHandler()
        self.listeners = {}
        self.bool = vool
        self.keys_old[key_.ESCAPE] = True
        self.batch = Batch()
        self.window = window
        self.scale = vec2(window.width / 1280., window.height / 720.)
        self.layout = MenuLayout(self.batch, self.scale)

    def update(self, dt):
        buttons = 0
        for key, button in self.layout:
            if button.over_button(*self.m_pos):
                button.highlight()
                buttons += 1
                try:
                    if self.keys[1338]:
                        self.handle_clicks(key)
                except KeyError:
                    continue
            else:
                button.restore()
        if not buttons and self.keys[1338] and not self.keys_old[1338]:
            self.handle_empty()
        self.add_update(dt)

        self.keys_old.update(self.keys)

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

    def draw(self):
        self.batch.draw()

    def handle_clicks(self, key):
        pass

    def handle_empty(self):
        pass

    def add_update(self, dt):
        pass

    def restore(self):
        self.layout.restore()
