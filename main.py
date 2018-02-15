#!/usr/bin/python3

import config
import loader

if __name__ == '__main__':
    cfg = config.Config()
    
    if not cfg.read():
        print('Could not read configuration')
        cfg.default()
    
    loader.load(cfg.get_array('providers', 'enabled'), cfg)
    
    loaded = loader.get_loaded()
    for provider in loaded.keys():
        cfg.inject(provider, loaded[provider].get_config())
        loaded[provider].start()
