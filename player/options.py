import json


colors = {'blue': (102, 217, 239),
          'red': (249, 38, 114),
          'green': (166, 226, 46)}

standards = {'name': 'UnnamedPlayer',
             'color': 'blue',
             'right': 'D',
             'left': 'A',
             'up': 'SPACE'}


class Options(object):
    """docstring for Options"""
    def __init__(self):
        super(Options, self).__init__()
        try:
            with open('.config', 'r') as f:
                self.odict = json.load(f)
        except IOError:
            self.odict = standards
            with open('.config', 'w') as f:
                json.dump(self.odict, f, indent=4)

    def __getitem__(self, key):
        return self.odict[key]

    def __setitem__(self, key, value):
        self.odict[key] = value

    def save(self):
        with open('.config', 'w') as f:
            json.dump(self.odict, f, indent=4)
