import zulip
import requests
import os
from pygtaw import wrapper

class TranslateBot(object):
    def __init__(self, translate_key):
        self.translate_key = translate_key
        self.client = zulip.Client(os.environ['ZULIP_EMAIL'],
                                   os.environ['ZULIP_KEY'])
        self.subscribe_all()

    def process_message(self, msg):
        content = msg['content'].split()
        sender_email = msg['sender_email']

        if sender_email == os.environ['ZULIP_EMAIL']:
            return

        if (content[0] == 'translate') or content[0] == '@**Translation**':
            target = content[1].capitalize()
            query = ' '.join(content[2:])

            pygtaw = wrapper.Client(self.translate_key)
            translation = pygtaw.translate(query, target)


            if msg['type'] == 'stream':
                self.client.send_message({
                    'type': 'stream',
                    'subject': msg['subject'],
                    'to': msg['display_recipient'],
                    'content': translation.translated_text
                })
            elif msg['type'] == 'private':
                self.client.send_message({
                    'type': 'private',
                    'to': msg['sender_email'],
                    'content': translation.translated_text
                })
            else:
                return

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