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
        self.http_pool = urllib3.PoolManager()
        self.resource_path = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__)) + '/resources/'
        
        self.prefix = 'UNKOWN'
        self.delay = 1
    
        self.value = ''
        self.new_hash = ''
        self.old_hash = ''
    
    
    
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
        
        notify2.init(self.prefix)
    
    def check(self):
        pass
    
    
    
    def run(self):
        while True:
            self.log('Checking')
            
            self.old_hash = self.new_hash
            self.check()
            
            self.value = str(self.value)
            self.new_hash = hashlib.md5(self.value.encode('utf-8')).hexdigest()
            
            if not self.new_hash == self.old_hash:
                self.notify()
            
            time.sleep(self.delay)
    
    def log(self, message):
        print('[' + self.prefix + '] ' + message)
    
    def notify(self):
        notice = notify2.Notification(self.prefix, self.value)
        
        if os.path.isfile(self.resource_path + self.prefix + '.png'):
            notice = notify2.Notification(self.prefix, self.value, 'file://' + self.resource_path + self.prefix + '.png')
        
        notice.set_timeout(5000)
        notice.show()
    
    def get_html(self, url):
        return bs(self.http_pool.request('GET', url).data.decode('utf-8'), 'lxml')
