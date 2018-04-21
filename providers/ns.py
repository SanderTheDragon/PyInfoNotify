from providers import provider

class Provider(provider.Base):
    def get_config(self):
        return {
            '; filter': 'Only show notification if any of the words is in the message, empty or * will show all notifications',
            'filter': [],
            '; maintenance': 'Also show maintenance messages',
            'maintenance': False
        }


    def init(self):
        self.name = 'NS Storingen'
        self.delay = '10m'

        return True



    def notification(self, icon, title, last_update, content):
        message  = '<img src=\"file://' + self.resource_path + 'ns_icon--' + icon + '.png\"/><br/>'
        message += '<u><b>' + title + '</b></u><br/>'
        message += '<b>' + last_update + '</b><br/><br/>'
        message += content
        message  = message[:-5] #Remove last <br/>

        return message


    def html_notification(self, icon, title, last_update, content):
        size = '2'
        if len(title) > 30:
            size = '3'
        elif len(title) > 44:
            size = '4'

        message  = '<span><img style=\"float: left;\" src=\"file://' + self.resource_path + 'ns_icon--' + icon + '.png\"/>'
        message += '<h' + size + ' style=\"margin: 0 40px; float: left;\">' + title + '</h2></span>'
        message += '<p style=\"margin-top: 16px;\">'
        message += '<h4 style=\"margin: 0;\">' + last_update + '</h4><br/>'
        message += content
        message  = message[:-5] #Remove last <br/>
        message += '</p>'

        return message



    def check(self):
        html = self.get_html('https://www.ns.nl/reisinformatie/actuele-situatie-op-het-spoor')

        for disruption in html.findAll('div', { 'class': 'grid__unit s-4-4 m-12-12 l-6-12' }):
            if not disruption.find('a').text.strip() == 'Alle werkzaamheden de komende maanden':
                title = disruption.find('a').text.strip()
                last_update = disruption.find('p', { 'class': 'overlayHeading__lastUpdate' }).text.strip().capitalize()
                content = str(disruption.findAll('div', { 'class': 'overlayContent' })[0].findAll('p')[0].decode_contents())

                if self.data['html'] == 'True':
                    message = self.html_notification('alert', title, last_update, content)
                else:
                    message = self.notification('alert', title, last_update, content)

                notify = False
                if len(self.data['filter']) == 0 or self.data['filter'] == '*':
                    notify = True
                else:
                    for key in self.data['filter'].split(' '):
                        if key in message:
                            notify = True
                            break

                if notify:
                    self.notifications.append(message)

        if self.data['maintenance'] == 'True':
            for maintenance in html.findAll('div', { 'class': 'grid__unit s-4-4 m-12-12 l-6-12 plannedDisruption' }):
                title = maintenance.find('a').text.strip()

                content = maintenance.findAll('div', { 'class': 'overlayContent' })[0]
                p_list = content.findAll('p')
                last_update = p_list[1].text.strip().capitalize() + ' ' + p_list[0].text.strip()

                content_text = p_list[2].text.strip() + '<br/>'

                li_list = content.findAll('ul')[0].findAll('li')
                for li in li_list:
                    text = li.text.strip()
                    text_list = list(text)
                    text_list[0] = text_list[0].upper()
                    text = ''.join(text_list)

                    content_text += '<b>-</b> ' + text + '<br/>'

                if self.data['html'] == 'True':
                    message = self.html_notification('maintenance', title, last_update, content_text)
                else:
                    message = self.notification('maintenance', title, last_update, content_text)

                notify = False
                if len(self.data['filter']) == 0 or self.data['filter'] == '*':
                    notify = True
                else:
                    for key in self.data['filter'].split(' '):
                        if key in message:
                            notify = True
                            break

                if notify:
                    self.notifications.append(message)
