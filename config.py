import configparser
import os
import sys

class Config:
    def __init__(self):
        self.parser = configparser.ConfigParser()
        self.config_file = os.path.join(os.path.expanduser('~'), '.inforc')
        
        if not os.path.isfile(self.config_file):
            self.default()
            self.write()
    
    def default(self):
        self.parser.add_section('providers')
        self.parser['providers']['enabled'] = 'knmi'
        
        for root, directories, files in os.walk(os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)) + '/providers/'):
            if root.endswith('providers/'):
                for filename in files:
                    if filename.endswith('.py') and not filename == 'provider.py':
                        self.parser.add_section('.'.join(filename.split('.')[:-1]))
    
    def inject(self, provider, dictionary):
        for key in dictionary.keys():
            self.parser[provider][key] = dictionary[key]
        
        self.write()
    
    def read(self):
        return self.parser.read(self.config_file)
    
    def write(self):
        with open(self.config_file, 'w') as stream:
            self.parser.write(stream)
    
    
    
    def get_data_dict(self):
        dictionary = {}
        
        for key in self.parser.keys():
            if not key == 'providers':
                dictionary[key] = self.parser[key]
        
        return dictionary
    
    def get_string(self, section, key):
        return self.parser[section][key]
    
    def get_array(self, section, key):
        return self.get_string(section, key).split(' ')
