import zulip
from papago import Papago
from config import NAVER_CLIENT_ID, NAVER_CLIENT_SECRET, ZULIP_EMAIL, ZULIP_KEY, ZULIP_SITE

class TranslateBot(object):
    def __init__(self):
        self.client = zulip.Client(email=ZULIP_EMAIL, api_key=ZULIP_KEY, site=ZULIP_SITE)
        self.papago = Papago(NAVER_CLIENT_ID, NAVER_CLIENT_SECRET)
        self.subscribe_all()

    def check_hangul(self, query):
        return any(u'\uac00' <= c <= u'\ud7a3' for c in query)

    def process_message(self, msg):
        content = msg['content']
        sender_email = msg['sender_email']

        if sender_email == ZULIP_EMAIL:
            return

        if self.check_hangul(content):
            translated_text = self.translate(content)
            translated_text = (f'**{msg["sender_full_name"]}** said:\n```` quote\n{content}\n````\n{translated_text}')
        else:
            translated_text = msg['content'] # repeat if no hangul

        if msg['type'] == 'stream':
            self.client.send_message({
                'type': 'stream',
                'subject': msg['subject'],
                'to': msg['display_recipient'],
                'content': translated_text
            })

    def translate(self, text, source="ko", target="en"):
        s = self.papago.translate(text, source, target)
        s.replace('```` ```` quote', '```` quote') # Papapgo handles quote incorrectly
        return s

    def subscribe_all(self):
        streams = [{'name': stream['name']} for stream in self.client.get_streams()['streams']]
        self.client.add_subscriptions(streams)


def main():
    bot = TranslateBot()
    bot.client.call_on_each_message(bot.process_message)

if __name__ == '__main__':
    main()