#!/usr/bin/python3

import config
import loader
import signal

loaded = {}
enabled_providers = []
cfg = config.Config()

def sig_usr1(signum, frame):
    print('[MAIN] SIGUSR1, force check providers')
    for provider in enabled_providers:
        loaded[provider].check()
        loaded[provider].notify_all()


def sig_usr2(signum, frame):
    print('[MAIN] SIGUSR2, reloading')
    for provider in enabled_providers:
        loaded[provider].stop.set()

    start()



def start():
    if not cfg.read():
        print('[MAIN] Failed to read configuration')
        cfg.default()

    loader.load(cfg)

    global loaded
    loaded = loader.get_loaded()
    for provider in loaded.keys():
        cfg.inject(provider, loaded[provider])

        if provider in cfg.get_array('providers', 'enabled'):
            enabled_providers.append(provider)
            loaded[provider].start()

    if len(enabled_providers) == 0:
        print('[MAIN] Add at least one provider in the configuration file')


if __name__ == '__main__':
    signal.signal(signal.SIGUSR1, sig_usr1)
    signal.signal(signal.SIGUSR2, sig_usr2)

    start()
