from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return {
            'province': 'zuid-holland'
        }
    
    def init(self):
        self.prefix = 'KNMI Waarschuwingen'
        self.delay = '1h'
        
        return True
    
    def check(self):
        html = self.get_html('http://knmi.nl/nederland-nu/weer/waarschuwingen/' + self.data['province'])
        
        for warning in html.findAll('div', { 'class': 'warning-overview' }):
            if not warning.find('h3').text == 'Geen waarschuwingen voor':
                message = ''
                
                color = ''
                if 'warning-overview--yellow' in warning.attrs['class']:
                    color = 'FFDE3C'
                elif 'warning-overview--orange' in warning.attrs['class']:
                    color = 'EF5D12'
                elif 'warning-overview--red' in warning.attrs['class']:
                    color = 'CE1F00'
                
                title = warning.find('h3')
                message += '<img style=\"float: left;\" src=\"file://' + self.resource_path + 'knmi_' + title.attrs['class'][-1] + '.png\" />'
                message += '<h2 style=\'margin: 0 40px; float: left; color: #' + color + ';\'>' + title.text + '</h2><br/>'
                
                message += warning.find('div', { 'class': 'warning-overview__description' }).decode_contents()
                message = message[:-5] #Remove last <br/>
                
                self.values.append(message)
