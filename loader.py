import importlib
import os
import traceback

loaded = {}

def load(config):
    providers = []
    for root, directories, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + '/providers/'):
        if root.endswith('providers/'):
            for filename in files:
                if filename.endswith('.py') and not filename == 'provider.py' and not filename == '__init__.py':
                    providers.append('.'.join(filename.split('.')[:-1]))

    for provider in providers:
        try:
            mod = importlib.import_module('.' + provider, 'providers')
            data = config.get_data_dict()[provider]

            data['html'] = config.get_string('notifications', 'html')
            data['timeout'] = config.get_string('notifications', 'timeout')

            loaded[provider] = mod.Provider(data)

            if not loaded[provider].init():
                print('[LOADER] Failed to initialize ' + provider)
                loaded[provider] = False

            if provider in config.get_array('providers', 'sound'):
                loaded[provider].sound = True

            loaded[provider].post_init()
        except ModuleNotFoundError:
            print('[LOADER] ' + provider + ' does not exist')
            loaded[provider] = False
        except:
            print('[LOADER] Failed to load module: ' + provider)
            traceback.print_exc()
            loaded[provider] = False



def get_loaded():
    dictionary = {}

    for key in loaded.keys():
        if not not loaded[key]:
            dictionary[key] = loaded[key]

    return dictionary
