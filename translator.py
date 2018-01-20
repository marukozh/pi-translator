# -*- coding: utf-8 -*-
import json
import requests
import urllib
import subprocess
import argparse
import pycurl
import StringIO
import os.path

def transcribe(language):
    key = ''  # Microsoft API key
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
        None

    def translate_text(self, phrase, origin_language, destination_language):
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
        translation = self.translate_text(text, origin_language, destination_language)
        self.speak_text('Translating ' + text, origin_language)
        print "Translation: ", translation
        self.speak_text(translation, destination_language)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Raspberry Pi - Translator.')
    parser.add_argument('-o', '--origin_language', help='Origin Language', required=True)
    parser.add_argument('-d', '--destination_language', help='Destination Language', required=True)
    args = parser.parse_args()
    while True:
        Translator().translate(args.origin_language, args.destination_language, transcribe(args.origin_language))
