import yaml

def load(src = 'example.yaml'):
    with open(src, 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
    for section in cfg:
        print (section)
    return cfg




