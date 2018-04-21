import certifi
import hashlib
import lxml
import notify2
import os
import simpleaudio
import threading
import time
import traceback
import urllib3
from bs4 import BeautifulSoup as bs

class Base(threading.Thread):
    stop = threading.Event()

    def __init__(self, data):
        threading.Thread.__init__(self)

        self.data = data
        self.http_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.resource_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)) + '/resources/'
        self.sound = False

        self.name = 'UNKOWN'
        self.delay = 1

        self.notifications = []
        self.hashes = []



    def get_config(self):
        return {}


    def init(self):
        return False


    def check(self):
        pass



    def post_init(self):
        if not type(self.delay) == int:
            delay = 0

            for part in self.delay.split(' '):
                amount = ''
                unit = ''

                for c in part:
                    if c.isdigit():
                        amount += c
                    else:
                        unit += c

                amount = int(amount)
                if unit == 'ms':
                    delay += amount * 0.001
                elif unit == 's':
                    delay += amount
                elif unit == 'm':
                    delay += amount * 60
                elif unit == 'h':
                    delay += amount * 60 * 60

            self.delay = delay



    def run(self):
        while not self.stop.is_set():
            sounded = False

            self.log('Checking')
            try:
                self.check()
                self.notify_all()

                time.sleep(self.delay)
            except:
                self.log('Something went wrong, retry in 5 seconds')
                traceback.print_exc()
                time.sleep(5)



    def notify_all(self):
        if type(self.notifications) == str:
            self.notifications = [ self.notifications ]

        for item in self.notifications:
            item_hash = hashlib.md5(item.encode('utf-8')).hexdigest()

            if not item_hash in self.hashes:
                if self.sound and not sounded and os.path.isfile(self.resource_path + self.name + '.wav'):
                    simpleaudio.WaveObject.from_wave_file(self.resource_path + self.name + '.wav').play()
                    sounded = True

                self.notify(item, item_hash)
                self.hashes.append(item_hash)



    def log(self, message):
        print('[' + self.name + '] ' + message)


    def notify(self, item, item_hash):
        notify2.init(self.name + item_hash)

        notice = notify2.Notification(self.name, item)

        if os.path.isfile(self.resource_path + self.name + '.png'):
            notice = notify2.Notification(self.name, item, 'file://' + self.resource_path + self.name + '.png')

        notice.set_timeout(int(self.data['timeout']))
        notice.show()



    def get_html(self, url):
        return bs(self.http_pool.request('GET', url).data.decode('utf-8'), 'lxml')
