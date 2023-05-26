# !/usr/bin/env python
# _*_coding:utf-8_*_

# 給任何使用這支程式的人：這支程式是國台語合成的API的client端。具體上會發送最下方變數data
# 給伺服器，並接收一個回傳的wav檔，output.wav

#客戶端 ，用來呼叫service_Server.py

import socket
import struct
import os
from datetime import datetime

class TTSClient: # for taiwanese
    def __init__(self):
        self.host = "140.116.245.157"

    ### Don't touch
    def askForService(self, data:str, dir_path: str , file_name: str = datetime.now().strftime("%H%M%S") + ".wav"): 
        '''
        Ask TTS server.
        Params:
            data        :(str) Text to be synthesized.
            file_name   :(str) File name to be stored.
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if not len(data):
                raise  ValueError ( "Length of data must be bigger than zero")
            
            sock.connect((self.host, self.__port))
            msg = bytes(self.__token + "@@@"+ data +'@@@'+ self.__model+'@@@'+ self.language, "utf-8")
            msg = struct.pack(">I", len(msg)) + msg
            sock.sendall(msg)

            if 'pinyin' in self.language:
                l = sock.recv(8192)
                l = l.decode('UTF-8').lstrip().rstrip()
                print(l)
                return l
            else:
                if not os.path.isdir(dir_path):
                    os.mkdir(dir_path)
                
                with open(dir_path + "/" + file_name,'wb') as f:
                    while True:
                        l = sock.recv(8192)
                        if not l: 
                            break
                        f.write(l)
                print("File received complete")
                return dir_path + "/" + file_name
                
        finally:
            sock.close()

    def set_language(self, language:str, model:str):
        '''
        Set port and token by language.
        Set model by gender.
        Params:
            language    :(str) chinese \
                or taiwanese or taiwanese_sandhi or tailuo or tailuo_sandhi or hakka.
            model       :(str) HTS synthesis model name.
        '''
        self.language = language

        if language == 'chinese':
            self.__port = 10015
            self.__token = "mi2stts"
            self.__model = 'M60'

        elif language == 'taiwanese' or language == 'tailuo':
            self.__port = 10011
            self.__token = "mi2stts"
            self.__model = model

        elif language == 'taiwanese_sandhi' or language == 'tailuo_sandhi':
            self.__port = 10012
            self.__token = "mi2stts"
            self.__model = model

        elif 'hakka' in language:
            self.__port = 10010
            self.__token = "mi2stts"
            self.__model = model

        else:
            raise  ValueError ( "'language' param must be chinese \
                or taiwanese or taiwanese_sandhi or tailuo or tailuo_sandhi or hakka." )
      

# if __name__=='__main__':
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--language', default='tailuo_sandhi', help='Language to be synthesized, \
    #     chinese or taiwanese or taiwanese_sandhi or tailuo or tailuo_sandhi or hakka.')
    # parser.add_argument('--model', default='M12', help='HTS synthesis model name.')
    # parser.add_argument('--data', default='gua2 kin1-a2-jit8 kho2-tshi3 te7-ji7-mia5', help='Text to be synthesized.') #input tailuo data
    # parser.add_argument('--o', default='output.wav', help='File name to be stored.') #output speech file
    # args = parser.parse_args()
    # tts_client = TTSClient()
    # tts_client.set_language(language=args.language, model=args.model)
    # tts_client.askForService(data = args.data, file_name=args.o)
# tts_client = TTSClient()
# tts_client.set_language(language="taiwanese_sandhi", model="M12")
# tts_client.askForService(data = "我是阿拉伯石油小公主", dir_path="./static/tts" ,file_name= "output.wav")

class TTSCrossLanguage: # for Chinese 

    def __init__(self):
        self.__host = "140.116.245.147"
        self.__port = 10000
        self.__token = "mi2stts"

    def askForService(self, text:str, dir_path: str , file_name: str = datetime.now().strftime("%H%M%S") + ".wav"):
        '''
        Ask cross language synthesis server.
        Params:
            text        :(str) Text to be synthesized. 
        '''
        if not len(text):
            raise ValueError ("Length of text must be bigger than zero")
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.__host, self.__port))
            msg = bytes(self.__token + "@@@" + text + '@@@' + self.__speaker + '@@@'+ self.__language, "utf-8")
            msg = struct.pack(">I", len(msg)) + msg
            sock.sendall(msg)
            
            with open(dir_path + "/" + file_name,'wb') as f:
                while True:
                    l = sock.recv(8192)
                    if not l: 
                        break
                    f.write(l)
            
            print("File received complete")
            return dir_path + "/" + file_name
        
        except Exception as e:
            print(e)
        
        finally:
            sock.close()

    def set_language(self, language:str, speaker:str):
        '''
        Params:
            language    :(str) Language to be synthesized, "tw" is Taiwanese or "zh" is Chinese or "en" is English.
            speaker     :(str) Target speaker to be synthesized.
        '''
        self.__language = language
        if self.__language not in ['tw', 'zh', 'en']:
            raise ValueError('Language must be "tw" or "zh" or "en".')
        
        if speaker:
            self.__speaker = speaker
        
        elif self.__language == 'tw':
            self.__speaker = 'F64'
        
        elif self.__language == 'zh':
            self.__speaker = 'F101'

        elif self.__language == 'en':
            self.__speaker = 'en10'

# if __name__=='__main__':
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--text', type=str, default='Today is Friday，要去台南走走', help='Text to be synthesized.')

#     parser.add_argument('--language', 
#                         type=str, 
#                         default='tw',
#                         choices=['tw', 'zh', 'en'], 
#                         help='Language to be synthesized, "tw" is Taiwanese, "zh" is Chinese or "en" is English.')
    
#     parser.add_argument('--speaker',
#                         type=str, 
#                         default='UDN', 
#                         choices=['F06', 'F07', 'F26', 'F52', 'F53', 'F64', 'F68',     # Taiwanese speaker
#                                  'F100','F101','F102','F103','F106','UDN',            # Chinese speaker
#                                  'en7', 'en9', 'en10','en11','en14','en16','en18'],   # English speaker
#                         help='Target speaker to be synthesized.')
#     args = parser.parse_args()
    
#     tts_client = TTSCrossLanguage()
#     tts_client.set_language(language=args.language, speaker=args.speaker)
#     tts_client.askForService(args.text)

# tts_client = TTSCrossLanguage()
# tts_client.set_language(language="tw", speaker="UDN")
# tts_client.askForService(text = "我是阿拉伯石油小公主",dir_path="./static/tts" )
