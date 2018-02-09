import time
from providers import provider

class Provider(provider.Base):
    def init(self):
        self.prefix = 'KNMI Waarschuwingen'
        self.delay = '10s'
        
        return True
    
    def check(self):
        self.value = self.get_html(self.data['url'])
        pass
