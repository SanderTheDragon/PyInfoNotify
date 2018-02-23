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
        self.delay = '1m'
        
        if not os.path.isdir(self.resource_path + 'nos_temp'):
            os.mkdir(self.resource_path + 'nos_temp')
        
        return True
    
    def check(self):
        html = self.get_html('https://nos.nl/')
        live_urls = []
        
        for li in html.findAll('li', { 'class': 'list-featured__item' }):
            badge = li.findAll('span', { 'class': 'badge' })
            if len(badge) > 0 and badge[0].text == 'liveblog':
                live_urls.append('https://nos.nl' + li.findAll('a')[0].attrs['href'])
        
        
        for li in html.findAll('li', { 'class': 'topstories__list-item' }):
            badge = li.findAll('span', { 'class': 'badge' })
            if len(badge) > 0 and badge[0].text == 'liveblog':
                live_urls.append('https://nos.nl' + li.findAll('a')[0].attrs['href'])
        
        for live_url in live_urls:
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
                    
                    tables = li.findAll('table')
                    if len(tables) > 0:
                        table = tables[0]
                        even = True
                        
                        message += '<h4>' + li.findAll('h2')[-1].text + '</h4>'
                        
                        message += '<table cellpadding=\"5\">'
                        for tr in table.findAll('tr'):
                            column_count = len(tr.findAll('td'))
                            
                            message += '<tr>'
                            if tr.parent.name == 'thead':
                                for td in tr.findAll('td'):
                                    if len(td.text) > 0:
                                        message += '<th>' + td.text + '</th>'
                                    else:
                                        message += '<th></th>'
                            else:
                                for td in tr.findAll('td'):
                                    if len(td.text) > 0:
                                        message += '<td>' + td.text + '</td>'
                            message += '</tr>'
                            
                            even = not even
                        message += '</table>'
                    
                    video = None
                    videos = desc.findAll('div', { 'class': 'block_video' })
                    if len(videos) > 0:
                        video = videos[0].findAll('a')[0]
                    
                    if self.data['images'] == 'True':
                        images = desc.findAll('img')
                        if len(images) > 0:
                            src = images[0].attrs['src']
                            image = self.download_image(src, title)
                            
                            if not video == None:
                                message += '<a href=\"https://nos.nl' + video.attrs['href'] + '\">'
                            
                            message += '<img src=\"file://' + image + '\" />'
                            
                            if not video == None:
                                message += '</a>'
                    elif not video == None:
                        message += '<a href=\"https://nos.nl' + video.attrs['href'] + '\">Video</a>'
                    
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
        
