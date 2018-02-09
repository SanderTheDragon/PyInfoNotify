import importlib

loaded = {}

def load(providers, data):
    for provider in providers:
        try:
            mod = importlib.import_module('.' + provider, 'providers')
            loaded[provider] = mod.Provider(data[provider])
            
            if not loaded[provider].init():
                print('Failed to initialize ' + provider)
                loaded[provider] = False
            
            loaded[provider].post_init()
        except ModuleNotFoundError:
            print('Could not load module ' + provider)
            loaded[provider] = False

def get_loaded():
    array = []
    
    for key in loaded.keys():
        if not not loaded[key]:
            array.append(loaded[key])
    
    return array
