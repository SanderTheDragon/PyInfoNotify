import time
from providers import provider

class Provider(provider.Base):
    def init(self):
        self.prefix = 'KNMI Waarschuwingen'
        self.delay = '10s'
        
        return True
    
    def check(self):
        self.value = [ '1', '2', '3' ]
        #self.get_html(self.data['url'])
        pass
