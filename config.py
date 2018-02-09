import configparser
import os

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
        
        for key in self.get_array('providers', 'enabled'):
            self.parser.add_section(key)
    
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
