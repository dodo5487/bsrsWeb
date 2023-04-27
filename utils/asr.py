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
    datas = {
        "token": "@@@bsrs@@@",
        "lang": "taiwanese",  # mandarin taiwanese
        "model_name": "TA_BSRS",  # mandarin taiwanese
        "audio_data": enc.decode('utf-8'),
        "source": "P"
    }

    r = requests.post('http://140.116.245.149:2802/asr', data=datas)

    # test
    # print(r.json().keys())
    # print(r.json()['status']) # True or False
    # print(r.json()['msg'])
    # print(r.json()['hyps'])
    print(r.json())
    return r.json()['words'][0]

