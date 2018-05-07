import yaml

class Jamla():

    def load(self, src='example.yaml'):
        with open(src, 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        for section in cfg:
            print (section)
        return cfg

    def get_primary_icons(self, jamla=None):
        """ Returns list of all static file paths """
        if jamla is None:
            raise Exception("get_primary_icons expects a jamla object")
        icons = []
        for item in jamla['items']:
            if item['primary_icon']['src']:
                icons.append(item['primary_icon']['src'])
        return icons




