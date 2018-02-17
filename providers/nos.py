import os
import shutil
from PIL import Image
from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return {
            'images': True,
            'limit': 3
        }
    
    def init(self):
        self.prefix = 'NOS Liveblog'
        self.delay = '5m'
        
        if not os.path.isdir(self.resource_path + 'nos_temp'):
            os.mkdir(self.resource_path + 'nos_temp')
        
        return True
    
    def check(self):
        html = self.get_html('https://nos.nl/')
        live_url = ''
        
        for li in html.findAll('li', { 'class': 'list-featured__item' }):
            badge = li.findAll('span', { 'class': 'badge' })
            if len(badge) > 0 and badge[0].text == 'liveblog':
                live_url = 'https://nos.nl' + li.findAll('a')[0].attrs['href']
        
        if len(live_url) > 0:
            html = self.get_html(live_url)
            updates = html.findAll('li', { 'class': 'liveblog__update' })
            if len(updates) > int(self.data['limit']):
                updates = updates[:int(self.data['limit'])]
            
            for li in updates:
                message = ''
                
                title = li.findAll('h2', { 'class': 'liveblog__update__title' })[0].text
                message = '<h3>' + title + '</h3>'
                
                desc = li.findAll('div', { 'class': 'liveblog__elements' })[0]
                for p in desc.findAll('p'):
                    message += '<p style=\"margin-top: 8px;\">' + p.decode_contents() + '</p>'
                
                if self.data['images'] == 'True':
                    images = desc.findAll('img')
                    if len(images) > 0:
                        src = images[0].attrs['src']
                        image = self.download_image(src, title)
                        message += '<img src=\"' + image + '\" />'
                
                self.values.append(message)
    
    def download_image(self, src, name):
        image = self.http_pool.request('GET', src, preload_content=False)
        ext = src.split('.')[-1]
        
        with open(self.resource_path + 'nos_temp/temp.' + ext, 'wb') as icon:
            shutil.copyfileobj(image, icon)
        
        img = Image.open(self.resource_path + 'nos_temp/temp.' + ext)
        width = 300
        ratio = float(width/float(img.size[0]))
        height = int(float(img.size[1]) * ratio)
        
        img = img.resize(( width, height ), Image.ANTIALIAS)
        img.save(self.resource_path + 'nos_temp/' + name + '.' + ext)
        os.remove(self.resource_path + 'nos_temp/temp.' + ext)
        
        return self.resource_path + 'nos_temp/' + name + '.' + ext
        
