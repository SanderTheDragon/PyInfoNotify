import configparser
import os

class Config:
    def __init__(self):
        self.parser = configparser.ConfigParser(comment_prefixes=( '#' ))
        self.config_file = os.path.join(os.path.expanduser('~'), '.inforc')

        if not os.path.isfile(self.config_file):
            self.default()
            self.write()



    def default(self):
        self.parser.add_section('providers')
        self.parser['providers']['; enabled'] = 'A list, separated by spaces, of providers which should be loaded'
        self.parser['providers']['enabled'] = ''
        self.parser['providers']['; sound'] = 'A list, separated by spaces, of providers which are allowed to play sound'
        self.parser['providers']['sound'] = ''

        self.parser.add_section('notifications')
        self.parser['notifications']['; html'] = 'Allow notifictions to use advanced HTML (your notifiction server may not support advanced HTML)'
        self.parser['notifications']['html'] = 'False'
        self.parser['notifications']['; timeout'] = 'Timeout for notifictions, in milliseconds'
        self.parser['notifications']['timeout'] = '5000'

        self.check_sections()



    def inject(self, provider, instance):
        dictionary = instance.get_config()

        if not provider in self.parser.keys():
            self.parser.add_section(provider)

        for key in dictionary.keys():
            if not key in self.parser[provider]:
                if type(dictionary[key]) == list:
                    self.parser[provider][key] = ' '.join(dictionary[key])
                    instance.data[key] = ' '.join(dictionary[key])
                else:
                    self.parser[provider][key] = str(dictionary[key])
                    instance.data[key] = str(dictionary[key])

        self.write()



    def check_sections(self):
        for root, directories, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/providers/'):
            if root.endswith('providers/'):
                for filename in files:
                    if filename.endswith('.py') and not filename == 'provider.py' and not filename == '__init__.py':
                        section = '.'.join(filename.split('.')[:-1])

                        if not section in self.parser.keys():
                            self.parser.add_section(section)



    def read(self):
        status = self.parser.read(self.config_file)
        self.check_sections()

        return status


    def write(self):
        with open(self.config_file, 'w') as stream:
            self.parser.write(stream)



    def get_data_dict(self, section=None):
        dictionary = {}

        if section is None:
            for key in self.parser.keys():
                dictionary[key] = self.get_data_dict(key)
        else:
            for key in self.parser[section].keys():
                dictionary[key] = self.parser[section][key]

        return dictionary


    def get_string(self, section, key):
        return self.parser[section][key]


    def get_array(self, section, key):
        return self.get_string(section, key).split(' ')
