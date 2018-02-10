import certifi
import hashlib
import lxml
import notify2
import os
import sys
import threading
import time
import urllib3
from bs4 import BeautifulSoup as bs

class Base(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        
        self.data = data
        self.http_pool = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        self.resource_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)) + '/resources/'
        
        self.prefix = 'UNKOWN'
        self.delay = 1
    
        self.values = []
        self.hashes = []
    
    
    
    def get_config(self):
        return {}
    
    def init(self):
        return False
    
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
    
    def check(self):
        pass
    
    
    
    def run(self):
        while True:
            self.log('Checking')
            self.check()
            
            if type(self.values) == str:
                self.values = [ self.values ]
            
            for item in self.values:
                item_hash = hashlib.md5(item.encode('utf-8')).hexdigest()
                
                if not item_hash in self.hashes:
                    self.notify(item, item_hash)
                    self.hashes.append(item_hash)
            
            time.sleep(self.delay)
    
    def log(self, message):
        print('[' + self.prefix + '] ' + message)
    
    def notify(self, item, item_hash):
        notify2.init(self.prefix + item_hash)
        
        notice = notify2.Notification(self.prefix, item)
        
        if os.path.isfile(self.resource_path + self.prefix + '.png'):
            notice = notify2.Notification(self.prefix, item, 'file://' + self.resource_path + self.prefix + '.png')
        
        notice.set_timeout(5000)
        notice.show()
    
    def get_html(self, url):
        return bs(self.http_pool.request('GET', url).data.decode('utf-8'), 'lxml')
