#!/usr/bin/python3

import config
import loader
import signal

loaded = {}

def sig_usr1(signum, frame):
    print('[MAIN] SIGUSR1, force check providers')
    for provider in loaded.keys():
        loaded[provider].log('Checking')
        loaded[provider].check()

if __name__ == '__main__':
    cfg = config.Config()
    
    if not cfg.read():
        print('Could not read configuration')
        cfg.default()
    
    signal.signal(signal.SIGUSR1, sig_usr1)
    
    loader.load(cfg.get_array('providers', 'enabled'), cfg)
    
    loaded = loader.get_loaded()
    for provider in loaded.keys():
        cfg.inject(provider, loaded[provider].get_config())
        loaded[provider].start()
