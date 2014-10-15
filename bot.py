import zulip
import requests
import os
from pygtaw import wrapper

class TranslateBot(object):
    def __init__(self, translate_key):
        self.client = zulip.Client(os.environ['ZULIP_EMAIL'],
                                   os.environ['ZULIP_KEY'])
        self.pygtaw = wrapper.Client(translate_key)
        self.subscribe_all()

    def process_message(self, msg):
        decoded_content = msg['content'].decode(encoding='utf-8')
        content = decoded_content.split()
        sender_email = msg['sender_email']

        if sender_email == os.environ['ZULIP_EMAIL']:
            return

        if content[0] == 'translate' or content[0] == '@**Translate**':
            target = content[1].capitalize()
            query = ' '.join(content[2:])
            translation = self.get_translation(query, target)


            if msg['type'] == 'stream':
                self.client.send_message({
                    'type': 'stream',
                    'subject': msg['subject'],
                    'to': msg['display_recipient'],
                    'content': translation.translated_text
                })
            else:
                self.client.send_message({
                    'type': 'private',
                    'to': msg['sender_email'],
                    'content': translation.translated_text
                })

    def get_translation(self, query, target):
        try:
            return self.pygtaw.translate(query, target)
        except KeyError:
            target = 'English'
            return self.pygtaw.translate(query, target)


    def subscribe_all(self):
        response = requests.get('https://api.zulip.com/v1/streams',
            auth=requests.auth.HTTPBasicAuth(os.environ['ZULIP_EMAIL'], os.environ['ZULIP_KEY'])
        )

        if response.status_code == 200:
            json = response.json()['streams']
            streams = [{'name': stream['name']} for stream in json]
            self.client.add_subscriptions(streams)
        else:
            raise Exception(response)

def main():
    bot = TranslateBot(os.environ['TRANSLATE_KEY'])
    bot.client.call_on_each_message(bot.process_message)


if __name__ == '__main__':
    main()