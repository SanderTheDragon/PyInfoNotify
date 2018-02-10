from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return {
            'filter': [],
            'maintenance': False
        }
    
    def init(self):
        self.prefix = 'NS Storingen'
        self.delay = '10m'
        
        return True
    
    def check(self):
        html = self.get_html('https://www.ns.nl/reisinformatie/actuele-situatie-op-het-spoor')
        
        for disruption in html.findAll('div', { 'class': 'grid__unit s-4-4 m-12-12 l-6-12' }):
            if not disruption.find('a').text.strip() == 'Alle werkzaamheden de komende maanden':
                message = ''
                
                message += '<span><img style=\"float: left;\" src=\"file://' + self.resource_path + 'ns_icon--alert.png\"/>'
                message += '<h3 style=\"margin: 0 40px; float: left;\">' + disruption.find('a').text.strip() + '</h3></span>'
                
                message += '<p style=\"margin-top: 16px;\">'
                message += '<h4 style=\"margin: 0;\">' + disruption.find('p', { 'class': 'overlayHeading__lastUpdate' }).text.strip().capitalize() + '</h4><br/>'
                message += str(disruption.findAll('div', { 'class': 'overlayContent' })[0].findAll('p')[0].decode_contents())
                message = message[:-5] #Remove last <br/>
                message += '</p>'
                
                notify = False
                if len(self.data['filter']) == 0 or self.data['filter'] == '*':
                    notify = True
                else:
                    for key in self.data['filter'].split(' '):
                        if key in message:
                            notify = True
                            break
                
                if notify:
                    self.value.append(message)
        
        
        
        if self.data['maintenance'] == 'True':
            for maintenance in html.findAll('div', { 'class': 'grid__unit s-4-4 m-12-12 l-6-12 plannedDisruption' }):
                message = ''
                
                message += '<span><img style=\"float: left;\" src=\"file://' + self.resource_path + 'ns_icon--maintenance.png\"/>'
                message += '<h4 style=\"margin: 0 40px; float: left;\">' + maintenance.find('a').text.strip() + '</h4></span>'
                
                content = maintenance.findAll('div', { 'class': 'overlayContent' })[0]
                p_list = content.findAll('p')
                
                message += '<p style=\"margin-top: 16px;\">'
                message += '<h4 style=\"margin: 0;\">' + p_list[1].text.strip().capitalize() + ' ' + p_list[0].text.strip() + '</h4><br/>'
                message += p_list[2].text.strip() + '<br/>'
                
                li_list = content.findAll('ul')[0].findAll('li')
                for li in li_list:
                    text = li.text.strip()
                    text_list = list(text)
                    text_list[0] = text_list[0].upper()
                    text = ''.join(text_list)
                    
                    message += '- ' + text + '<br/>'
                
                message = message[:-5] #Remove last <br/>
                message += '</p>'
                
                notify = False
                if len(self.data['filter']) == 0 or self.data['filter'] == '*':
                    notify = True
                else:
                    for key in self.data['filter'].split(' '):
                        if key in message:
                            notify = True
                            break
                
                if notify:
                    self.value.append(message)
