import os
import shutil
from PIL import Image
from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return {
            '; images': 'Download and resize images',
            'images': True,
            '; limit': 'Only show this amount of new notifications',
            'limit': 3,
            '; exclude': 'Don\'t show liveblog notifications if they fall in any of the categories',
            'exclude': []
        }


    def init(self):
        self.name = 'NOS Liveblog'
        self.delay = '1m'

        if not os.path.isdir(self.resource_path + 'nos_temp'):
            os.mkdir(self.resource_path + 'nos_temp')

        return True



    def check(self):
        html = self.get_html('https://nos.nl/')
        live_urls = [ ]

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

                skip = False
                metas = html.findAll('div', { 'class': 'liveblog-header__meta__item' })
                for meta in metas:
                    meta_items = []
                    if ', ' in meta.text:
                        meta_items = meta.text.split(', ')
                    else:
                        meta_items = [ meta.text ]

                    for meta_item in meta_items:
                        if meta_item in self.data['exclude'].split(' '):
                            skip = True

                if skip:
                    continue

                updates = html.findAll('li', { 'class': 'liveblog__update' })
                if len(updates) > int(self.data['limit']):
                    updates = updates[:int(self.data['limit'])]

                for li in updates:
                    message = ''

                    title = li.findAll('h2', { 'class': 'liveblog__update__title' })[0].text
                    if self.data['html'] == 'True':
                        message = '<h3>' + title + '</h3>'
                    else:
                        message = '<u><b>' + title + '</b></u><br/><br/>'

                    desc = li.findAll('div', { 'class': 'liveblog__elements' })[0]
                    for p in desc.findAll('p'):
                        if self.data['html'] == 'True':
                            message += '<p style=\"margin-top: 8px;\">' + p.decode_contents() + '</p>'
                        else:
                            message += p.decode_contents() + '<br/><br/>'

                    tables = li.findAll('table')
                    if len(tables) > 0:
                        table = tables[0]

                        if self.data['html'] == 'True':
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
                                        else:
                                            message += '<td></td>'
                                message += '</tr>'
                            message += '</table>'
                        else:
                            message += '<b>' + li.findAll('h2')[-1].text + '</b><br/>'

                            table_data = []
                            trs = table.findAll('tr')
                            for i in range(len(trs)):
                                tds = trs[i].findAll('td')
                                for j in range(len(tds)):
                                    if i == 0:
                                        table_data.append([])

                                    table_data[j].append(tds[j].text.strip())

                            from gi.repository import Gtk
                            from PIL import ImageDraw, ImageFont

                            label = Gtk.Label('')
                            label_style = label.get_style()
                            ( col_r, col_g, col_b ) = label.get_style_context().get_color(Gtk.StateFlags.NORMAL).to_color().to_floats()
                            ( font, size ) = label_style.font_desc.to_string().rsplit(' ', 1)

                            font_path = ''
                            for root, dirs, files in os.walk('/usr/share/fonts/truetype'):
                                if (font.replace(' ', '') + '-Regular.ttf') in files:
                                    font_path = os.path.join(root, font.replace(' ', '') + '-Regular.ttf')

                            image = Image.new('RGBA', ( 1204, 1024 ))
                            draw = ImageDraw.Draw(image)
                            image_font = ImageFont.truetype(font_path, int(size))

                            max_width = 0
                            x = 8
                            y = 8

                            for row in range(len(table_data[0])):
                                for column in range(len(table_data)):
                                    ( width, height ) = draw.textsize(max(table_data[column], key=len), font=image_font)

                                    draw.text(( x, y ), table_data[column][row], font=image_font, fill=( int(col_r), int(col_g), int(col_b), 255 ))
                                    x += width + 8
                                    if x > max_width:
                                        max_width = x
                                x = 8
                                y += 20

                            max_width += 8

                            image = image.crop(( 0, 0, max_width, y ))
                            image.save(self.resource_path + 'nos_temp/table-' + title + '.png')

                            message += '<img src=\"file://' + self.resource_path + 'nos_temp/table-' + title + '.png' + '\" />'

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

                            message += '<img style=\"margin-top: 8px;\" src=\"file://' + image + '\" />'

                            if not video == None:
                                message += '</a>'
                    elif not video == None:
                        message += '<a href=\"https://nos.nl' + video.attrs['href'] + '\">Video</a>'

                    self.notifications.append(message)


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
