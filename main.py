#!/usr/bin/python3

import config
import loader

if __name__ == '__main__':
    cfg = config.Config()
    
    if not cfg.read():
        print('Could not read configuration')
        cfg.default()
    
    loader.load(cfg.get_array('providers', 'enabled'), cfg.get_data_dict())
    
    for provider in loader.get_loaded():
        provider.start()
