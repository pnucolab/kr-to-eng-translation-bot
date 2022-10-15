import os
import sys
import urllib.request
import json

class Papago:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
    
    def translate(self, text, source="ko", target="en"):
        encText = urllib.parse.quote(text)
        data = "source=" + source + "&target=" + target + "&text=" + encText
        url = "https://openapi.naver.com/v1/papago/n2mt"

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", self.client_id)
        request.add_header("X-Naver-Client-Secret", self.client_secret)
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
        rescode = response.getcode()

        if rescode != 200:
            raise RuntimeError("Error Code: " + rescode)
        
        return json.loads(response.read().decode('utf-8'))["message"]["result"]["translatedText"]