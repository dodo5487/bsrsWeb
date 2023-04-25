import speech_recognition as sr
import requests
import base64

def stt_chinese(filePath):
    r = sr.Recognizer()
    wav = sr.AudioFile(filePath)
    with wav as source:
        audio = r.record(source)
    return r.recognize_google(audio, language = 'zh-tw')


def stt_taiwanese(filePath):

    enc = base64.b64encode(open(filePath, "rb").read())

    '''
    lang (must-have) (mandarin - 國語 / taiwanese - 台語)
    model (optional) 如不設定，將值設定成空字串
    '''
    data = {
        "token": "XXX",
        "lang": "taiwanese",  # mandarin taiwanese
        "model": "",  # mandarin taiwanese
        "audio_data": enc.decode('utf-8'),
        "audio_name": "Temporary"
    }

    r = requests.post('http://140.116.245.157:9500/asr', json=data)

    # test
    # print(r.json().keys())
    # print(r.json()['status']) # True or False
    # print(r.json()['msg'])
    # print(r.json()['hyps'])

    return r.json()['hyps']['result']

