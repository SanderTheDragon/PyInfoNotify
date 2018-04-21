from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return {
            '; province': 'The province to show warnings for',
            'province': 'utrecht'
        }


    def init(self):
        self.name = 'KNMI Waarschuwingen'
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
                if not self.data['html'] == 'True':
                    message += '<br/><br/>'

                if self.data['html'] == 'True':
                    message += '<h2 style=\'margin: 0 40px; float: left; color: #' + color + ';\'>' + title.text + '</h2><br/>'
                else:
                    code = 'Code Geel' if color == 'FFDE3C' else 'Code Oranje' if color == 'EF5D12' else 'Code Rood'
                    message += '<b><i>' + code + '</i><br/><u>' + title.text + '</u></b><br/><br/>'

                message += warning.find('div', { 'class': 'warning-overview__description' }).decode_contents()

                timelines = warning.findAll('div', { 'class': 'warning-timeline__section' })
                if len(timelines) > 0:
                    if not '<p>' in message or not self.data['html'] == 'True': #A P tag already adds enough spacing
                        message += '<br/>'

                    days = warning.findAll('div', { 'class': 'warning-timeline__day' })
                    for timeline in timelines:
                        if not '<p>' in message or not self.data['html'] == 'True': #A P tag already adds enough spacing
                            message += '<br/>'

                        message += 'Vanaf ' + days[int(timeline.attrs['data-from-day'])].text + ' ' + timeline.attrs['data-from-time'] + ' tot ' + days[int(timeline.attrs['data-until-day'])].text + timeline.attrs['data-until-time']

                self.notifications.append(message)
