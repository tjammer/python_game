from pyglet.window import Window, get_platform
from pyglet.graphics import Group


wmodes = ['windowed', 'windowed_fs', 'fullscreen']


def get_window(options):
    vsync = (options['vsync'] != '0')
    if options['wmode'] == 'windowed':
        return Window(1280, 720, vsync=vsync,
                      style=Window.WINDOW_STYLE_DEFAULT)
    elif options['wmode'] == 'windowed_fs':
        defa = get_platform() .get_default_display() .get_default_screen()
        w = defa.width
        h = defa.height
        return Window(w, h, vsync=vsync, style=Window.WINDOW_STYLE_BORDERLESS)
    elif options['wmode'] == 'fullscreen':
        return Window(vsync=vsync, fullscreen=True)
    else:
        return Window(1280, 720, vsync=vsync,
                      style=Window.WINDOW_STYLE_DEFAULT)


class CustomGroup(Group):
    """docstring for CustomGroup"""
    def __init__(self, arg):
        super(CustomGroup, self).__init__()
        self.ord = arg

    def __cmp__(self, other):
        if isinstance(other, CustomGroup):
            if self.ord > other.ord:
                return 1
            elif self.ord < other.ord:
                return -1
            else:
                return 0
        else:
            return self.ord
