import importlib

loaded = {}

def load(providers, config):
    for provider in providers:
        try:
            mod = importlib.import_module('.' + provider, 'providers')
            loaded[provider] = mod.Provider(config.get_data_dict()[provider])
            
            if not loaded[provider].init():
                print('Failed to initialize ' + provider)
                loaded[provider] = False
            
            if provider in config.get_array('providers', 'sound'):
                loaded[provider].sound = True
            
            loaded[provider].post_init()
        except ModuleNotFoundError:
            print('Could not load module ' + provider)
            loaded[provider] = False

def get_loaded():
    dictionary = {}
    
    for key in loaded.keys():
        if not not loaded[key]:
            dictionary[key] = loaded[key]
    
    return dictionary
