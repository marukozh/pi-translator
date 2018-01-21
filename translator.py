# -*- coding: utf-8 -*-
import json
import requests
import urllib
import subprocess
import argparse
import pycurl
import StringIO
import os.path
import time
import xml.etree.ElementTree

def get_microsoft_token():
    key = '' # Microsoft Translator Text API Key
    url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    c = pycurl.Curl()
    c.setopt(pycurl.VERBOSE, 0)
    c.setopt(pycurl.URL, url)
    c.setopt(pycurl.POSTFIELDSIZE, 0)
    fout = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, fout.write)
    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, ['Ocp-Apim-Subscription-Key: ' + key])
    c.perform()
    response_data = fout.getvalue()
    return response_data

def transcribe(language):
    key = ''  # Microsoft Speech Recognition API key
    stt_url = 'https://speech.platform.bing.com/speech/recognition/interactive/cognitiveservices/v1?language=' + language
    filename = 'test.wav'
    print "listening .."
    os.system(
        'arecord -D plughw:0,0 -f cd -c 1 -t wav -d 0 -q -r 16000 -d 3 ' + filename)
    print "interpreting .."
    # send the file to google speech api
    c = pycurl.Curl()
    c.setopt(pycurl.VERBOSE, 0)
    c.setopt(pycurl.URL, stt_url)
    fout = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, fout.write)

    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, ['Content-Type: audio/wav; codec=audio/pcm; samplerate=16000;', 'Ocp-Apim-Subscription-Key: ' + key])

    file_size = os.path.getsize(filename)
    c.setopt(pycurl.POSTFIELDSIZE, file_size)
    fin = open(filename, 'rb')
    c.setopt(pycurl.READFUNCTION, fin.read)
    c.perform()

    response_data = fout.getvalue()
    print 'response_data'
    print response_data
    result = json.loads(response_data)
    c.close()
    return result['DisplayText']


class Translator(object):

    def __init__(self):
        self.token_expiration_time = time.clock() + 9 * 60 # refresh token after 9 min.
        self.auth_token = get_microsoft_token()

    def ms_translate_text(self, phrase, origin_language, destination_language):
        url = 'https://api.microsofttranslator.com/V2/Http.svc/Translate?appid='
        c = pycurl.Curl()
        c.setopt(pycurl.VERBOSE, 0)
        c.setopt(pycurl.URL, url)
        c.setopt(pycurl.POSTFIELDSIZE, 0)
        fout = StringIO.StringIO()
        c.setopt(pycurl.WRITEFUNCTION, fout.write)
        if time.clock() > self.token_expiration_time:
            print "Refreshing Token..."
            self.token_expiration_time = time.clock() + 9 * 60
            self.auth_token = get_microsoft_token()
        header = 'Bearer%%20%s&from=%s&to=%s&text=%s' % (
        self.auth_token, origin_language, destination_language, phrase)
        request_url = url + header
        r = requests.get(request_url)
        result_text = r.text.encode('utf-8')
        e = xml.etree.ElementTree.fromstring(result_text)
        return e.text

    def google_translate_text(self, phrase, origin_language, destination_language):
        tts_url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=%s&tl=%s&dt=t&q=%s" % (origin_language, destination_language, phrase)
        print "translate url = " + tts_url
        r = requests.get(tts_url)
        result_text = r.text
        print result_text
        result = json.loads(result_text)[0][0][0]
        return result

    def speak_text(self, phrase, language):
        speech_url = "http://translate.google.com/translate_tts?ie=UTF-8&total=1&client=tw-ob&q=%s&tl=%s" % (phrase, language)
        subprocess.call(["mplayer", speech_url], shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def translate(self, origin_language, destination_language, text):
        translation = self.ms_translate_text(text, origin_language,
                                             destination_language)
        self.speak_text('Translating', 'en-US')
        self.speak_text(text, origin_language)
        print "Translation: ", translation
        self.speak_text(translation, destination_language)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Raspberry Pi - Translator.')
    parser.add_argument('-o', '--origin_language', help='Origin Language', required=True)
    parser.add_argument('-d', '--destination_language', help='Destination Language', required=True)
    args = parser.parse_args()
    while True:
        Translator().translate(args.origin_language, args.destination_language, transcribe(args.origin_language))
