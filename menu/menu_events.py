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
