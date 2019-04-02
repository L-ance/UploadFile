import configparser


class MyConfigParser(configparser.ConfigParser):
    def __init__(self, defaults=None):
        configparser.ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr

    def write(self, fp, space_around_delimiters=False):
        super().write(fp, space_around_delimiters=False)
