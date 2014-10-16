import zulip
import requests
import os
import HTMLParser
from pygtaw import wrapper

class TranslateBot(object):
    def __init__(self, translate_key):
        self.client = zulip.Client(os.environ['ZULIP_EMAIL'],
                                   os.environ['ZULIP_KEY'])
        self.pygtaw = wrapper.Client(translate_key)
        self.subscribe_all()

    def process_message(self, msg):
        content = msg['content'].split()
        sender_email = msg['sender_email']

        if sender_email == os.environ['ZULIP_EMAIL']:
            return

        if content[0] == 'translate' or content[0] == '@**Translate**':
            target, query = self.handle_chinese_and_haitian(content[1:])
            translation = self.get_translation(query, target)
            translated_text = self.handle_mentions(translation.translated_text)
            translated_text = self.unescape_html_entities(translated_text)
            if msg['type'] == 'stream':
                self.client.send_message({
                    'type': 'stream',
                    'subject': msg['subject'],
                    'to': msg['display_recipient'],
                    'content': translated_text
                })
            else:
                self.client.send_message({
                    'type': 'private',
                    'to': msg['sender_email'],
                    'content': translated_text
                })

    def handle_chinese_and_haitian(self, content):
        if content[0] in ['Chinese', 'Haitian']:
            target = ' '.join(content[0:2]).title()
            query = ' '.join(content[2:])
            return target, query
        else:
            target = content[0].capitalize()
            query = ' '.join(content[1:])
            return target, query

    def handle_mentions(self, translation):
        return translation.replace('@ ** ', '@**').replace(' **', '**')

    def get_translation(self, query, target):
        try:
            return self.pygtaw.translate(query, target)
        except KeyError:
            target = 'English'
            return self.pygtaw.translate(query, target)

    def unescape_html_entities(self, translated_text):
        html_parser = HTMLParser.HTMLParser()
        try:
            return html_parser.unescape(translated_text)
        except AttributeError:
            return translated_text


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