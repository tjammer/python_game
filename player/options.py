import json


colors = {'blue': (0, 204, 255),
          'red': (249, 38, 114),
          #'green': (166, 226, 46)}
          'green': (40, 40, 40)}

standards = {'name': 'UnnamedPlayer',
             'color': 'blue',
             'right': 'D',
             'left': 'A',
             'up': 'SPACE',
             'att': 'M1',
             'rdy': 'F3',
             'melee': '_1',
             'sg': '_2',
             'lg': 'E',
             'blaster': 'Q',
             'gl': 'R',
             'chat': 'ENTER',
             'wmode': 'windowed',
             'vsync': '1'}


class Options(object):
    """docstring for Options"""
    def __init__(self):
        super(Options, self).__init__()
        try:
            with open('.config', 'r') as f:
                self.odict = json.load(f)
                for key in standards:
                    try:
                        self.odict[key]
                    except KeyError:
                        self.odict[key] = standards[key]
        except IOError:
            self.odict = standards
            with open('.config', 'w') as f:
                json.dump(self.odict, f, indent=4)

    def __getitem__(self, key):
        return self.odict[key]

    def __setitem__(self, key, value):
        self.odict[key] = value

    def __iter__(self):
        return self.odict.itervalues()

    def iteritems(self):
        return self.odict.iteritems()

    def save(self):
        with open('.config', 'w') as f:
            json.dump(self.odict, f, indent=4)
