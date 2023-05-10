# -*- coding: UTF-8 -*-
import os, json , random , time 
import requests as req
from flask import Flask, jsonify, render_template, session , request, redirect , url_for
from flask_cors import CORS
from datetime import timedelta
from utils import hts_synthesis_client, asr
from datetime import datetime
import glob
import moviepy.editor as moviepy



othersSentences = [
    ["您好，這裡是輔助診斷聊天機器人。等一下會詢問一些問題，請你回想近一個禮拜的狀況，並請你以直覺回答就可以了"],

    ["請問最近生活中有沒有遇到什麼困難?",
    "請問你有些什麼煩惱或是壓力嗎?",
    "請問你是從事甚麼樣的工作的?"],

    ["好的，我這邊大致了解狀況了。謝謝你今天的訪談。請按右上上傳資料進行問卷上傳。"]
]

basicSentences = [
    ["你的睡眠上有什麼問題嗎? 比如說容易早醒或是難睡?",
    "你覺得自己的睡眠品質如何? 會不會比較有難以入睡或是怎麼樣的症狀",
    "你有睡眠障礙的症狀嗎? 有沒有感到疲倦或困倦?",
    "你是否有過入睡困難或是早醒的情況?"],

    ["你有感覺緊張不安的情況嗎?",
    "你會感到焦慮、恐懼或是緊張不安，這些情緒是否會影響到你的生活?",
    "你會對生活中的哪些事情感覺到緊張不安嗎?",
    "你有感覺到焦慮惶恐的情況嗎"],

    ["你有感覺容易苦惱或動怒的情況嗎?",
    "你會感到憤怒或是苦惱嗎? 如果有這些情緒是否會影響到你的生活?",
    "你會在什麼情況底下感到苦惱或是容易動怒嗎?",
    "你有感覺容易陷入煩惱或生氣的情況嗎"],

    ["你感覺心情怎麼樣，會不會有比較憂鬱的情況?",
    "你有感覺憂鬱、心情低落的情況嗎?",
    "你會感到悲傷、無助、無望，這些情緒是否會影響到你的生活?",
    "你有感覺情緒低落或沮喪的情況嗎"],

    ["你會有比不上別人的感覺嗎?",
    "你會覺得別人比較厲害，自己追不上的感覺嗎?",
    "你會有差人家一等的感覺嗎?",
    "你有感覺自己與他人相比有所不及的情況嗎?"],

    ["你會有想自殺的想法嗎?",
    "你會有想不開的念頭嗎?",
    "你會覺得沒什麼希望而想要自殺嗎?",
    "你會有嚴重的絕望感甚至到想要自殺嗎?"],

    ["你是否對大多數的事物比較感受不到興趣，或是對於過去大部份時間應會覺得愉快的事情，比較不能感受到樂趣?",
     "你是否對大多數的事物比較感受不到興趣，或是對於過去大部份時間應會覺得愉快的事情，比較不能感受到樂趣?",
     "你是否對大多數的事物比較感受不到興趣，或是對於過去大部份時間應會覺得愉快的事情，比較不能感受到樂趣?",
     "你是否對大多數的事物比較感受不到興趣，或是對於過去大部份時間應會覺得愉快的事情，比較不能感受到樂趣?"],

    ["你的食慾是否差不多每天都是下降或是增加，你的體重是否在不刻意增減的情況下有所改變?",
     "你的食慾是否差不多每天都是下降或是增加，你的體重是否在不刻意增減的情況下有所改變?",
     "你的食慾是否差不多每天都是下降或是增加，你的體重是否在不刻意增減的情況下有所改變?",
     "你的食慾是否差不多每天都是下降或是增加，你的體重是否在不刻意增減的情況下有所改變?"],

    ["你是否幾乎每天說話或是行動比平常遲緩？或是覺得煩躁，無法平靜，或是坐立不安呢?",
     "你是否幾乎每天說話或是行動比平常遲緩？或是覺得煩躁，無法平靜，或是坐立不安呢?",
     "你是否幾乎每天說話或是行動比平常遲緩？或是覺得煩躁，無法平靜，或是坐立不安呢?",
     "你是否幾乎每天說話或是行動比平常遲緩？或是覺得煩躁，無法平靜，或是坐立不安呢?"],

    ["你是否幾乎每天都覺得疲倦，缺乏精力?",
     "你是否幾乎每天都覺得疲倦，缺乏精力?",
     "你是否幾乎每天都覺得疲倦，缺乏精力?",
     "你是否幾乎每天都覺得疲倦，缺乏精力?"],

    ["你是否幾乎每天都覺得難以專心或下決定?",
     "你是否幾乎每天都覺得難以專心或下決定?",
     "你是否幾乎每天都覺得難以專心或下決定?",
     "你是否幾乎每天都覺得難以專心或下決定?"]

]

intensitySentences = [
    ["那你的睡眠品質從0到4分，0分代表完全沒有問題，4分代表有很嚴重的睡眠問題，你會給自己多少分呢?"],
    ["如果要你給出0到4分的分數，0分代表沒有緊張不安，1分代表輕微緊張不安，以此類推，4分代表總是緊張不安。這樣的話你會給自己幾分?"],
    ["那你覺得苦惱或動怒這件事0分代表完全沒有，1分代表輕微，2分代表中等，3分代表厲害，4分代表非常厲害。你覺得你會給自己幾分?"],
    ["那你覺得心情0到4分，0分代表沒有心情不好，4分代表心情總是很差，你會給自己幾分?"],
    ["那你覺得比不上別人這件事0分代表完全沒有，1分代表輕微，2分代表中等，3分代表厲害，4分代表非常厲害。你覺得你會給自己幾分?"],
    ["所以對於自殺的想法，你會給到自己幾分? 0分代表完全沒有想法，1分代表輕微，2分代表中等，3分代表厲害，4分代表非常厲害。"]
]

questionTypeKeywords = [
            ["睡眠","入睡","睡","醒","早醒","睡覺","睡著","嚇醒","易醒","惡夢","作夢","做夢","夢"],
            ["緊張","不安","坐立難安","焦慮","恐懼","恐懼"],
            ["苦惱","動怒","憤怒","生氣","煩惱","煩","愁","苦悶","惱","發愁","心煩","心煩意亂","煩亂","氣","惱怒","發火","發怒"],
            ["憂鬱","慮","憂心","鬱悶","難過","感傷","憂愁"],
            ["落後","不如","不及","遜色","比不上","中下","望塵莫及","不到"],
            ["自殺","輕生","想不開","自盡","燒炭","上吊","殺","自刎","自殘","想不開"],
            ["興趣","樂趣"],
            ["體重","重量","體態"],
            ["精神","遲緩","慢","激動"],
            ["專心","決定"]
            ]



symptomTypeKeywords = [["睡不好","作惡夢","做惡夢","淺眠","早醒","易醒","失眠"],
                       ["緊張","不安","緊張不安","坐立難安","焦慮","恐懼","恐懼"],
                       ["苦惱","動怒","憤怒","生氣","煩惱","抑鬱","苦悶","發愁","心煩","心煩意亂","煩亂","惱怒","發火","發怒"],
                       ["憂鬱","憂心","鬱悶","難過","感傷","憂愁","抑鬱"],
                       [],
                       ["自殺","輕生","想不開","自盡","上吊","自刎","自殘","想不開","想死","想不開"]
                       ]

replyWords = ["好的，","了解，","好的我了解了，","那我大概知道了，","嗯，","所以","好的，那","了解，那","","","","","",""]

eventTypeKeywords = [["籃球","桌球","棒球","爬山","攝影","打球","跑山","跑步","健走","登山","騎腳踏車","露營","排球"],
                     ["電影","小說","桌遊","音樂","流行樂","電視"],
                     ["手遊","電腦","電動","電競"],
                     ["考試","研究所","課業","作業","論文","期中考","期末考","期中","期末","學校"],
                     ["上班","下班","長官","領導","工作","老闆","上司",],
                     ["貓咪","貓","小狗","狗狗","小貓","寵物","動物"],
                     ["美食","牛排","咖啡","甜點","好吃","披薩","漢堡","壽司","火鍋","炸雞"],
                     ["經濟","沒錢","錢","薪水"],
                     ["父母","小孩","孩子","爸爸","父親","媽媽","母親"],
                     ["伴侶","男朋友","女朋友","女伴","男伴","另一半"],
                     ["喝酒","酗酒"],
                     ]

eventSentences = [["對於戶外運動來說，最熱門的運動之一就是籃球了。假日跟朋友一起去高中籃球場打一個下午，酣暢淋漓的感覺總是讓人感到舒服。你還有特別喜歡的運動嗎?"],
                  ["有時候不想動的時候聽一聽古典樂，可以讓心靈感到無比的放鬆。對於一些靜態的活動，你都會做什麼呢?"],
                  ["比起實體運動比賽，有時候電競比賽更吸引人。看著自己喜歡的選手，表現著精湛的操作，都會讓人感到緊張刺激。那你也喜歡電子競技嗎?"],
                  ["校園生活充滿了酸甜苦辣，小時候總希望能夠早點長大不要讀書。等到出了社會反而懷念起了當學生的單純。你可以多跟我分享一點你的校園生活或是課業上的問題嗎?"],
                  ["工作大概是人生中的一大部分，很多人應該都對它又愛又恨吧? 我想知道你的理想工作是甚麼呢? 你願意跟我分享嗎?"],
                  ["養寵物真的是一種很令人療育的事情。很多人在養貓之前是一個純粹的狗派，但是在養貓之後體驗到了養貓咪的方便! 你是貓派還是狗派又或者什麼派呢?"],
                  ["在早上的咖啡廳，點上一杯熱美式加上提拉米蘇邊吃邊工作。甜食跟咖啡已經佔據了很多人生活中的一大部分了。你有甚麼喜歡或是推薦的美食嗎?"],
                  ["錢不是萬能的，但是沒有錢卻是萬萬不能的。如果你有錢了，你第一件事最想做甚麼呢?"],
                  ["在家庭之中，不管是父母還是孩子，最重要的就是好好溝通。家庭之間如果有了矛盾，應該好好的大家坐下來談一下! 你願意跟我分享更多有關於你的家庭嗎?"],
                  ["情侶之間如果有矛盾的話，最好的解決辦法就是溝通了。如果一方一直憋在心裡，這樣的愛情很難長久。你願意跟我分享一下嗎?"],
                  ["跟許久不見的朋友小酌一杯，一起聊個天，享受微醺的感覺，絕對是人生中一件快樂的事情。但是還是要提倡理性飲酒! 所以你喝酒是為了甚麼呢?"]
                  ]

TOKEN = "mytoken"


def detectSentenceType(ws):
    
    nowQ = None
    for voc in ws:
        for questionTypeId in range(len(questionTypeKeywords)):
            for keyword in questionTypeKeywords[questionTypeId]:
                if voc == keyword:
                    if nowQ == None:
                        nowQ =  "q" + str(questionTypeId + 1)
                        break
            if nowQ != None:
                break
        if nowQ != None:
                break
        
    if session["user"]["preStep"] == "chit" and nowQ == None: # 第一次且找不到使用者回答的問句種類 => 直接 return steps[0]
        return session["user"]["steps"][0]
    elif session["user"]["preStep"] == "chit" and nowQ != None: # 第一次且有偵測到問句種類 => 直接 return nowQ
        return nowQ
    elif session["user"]["preStep"] != None and nowQ == None: # 前一次有問句種類這次沒有 
        if session["user"]["isFinishedQuestions"][session["user"]["preStep"]] == False: # 確認前一次結束沒 如果沒結束繼續問
            return session["user"]["preStep"]
        else: # 如果結束了 從steps中找下一個問題
            for step in session["user"]["steps"]:
                if session["user"]["isFinishedQuestions"][step] == False:
                    return step
    else: # 前一次跟這一次都有偵測到種類 
        if session["user"]["preStep"] == nowQ: # 前一次跟這一次都一樣種類  @@後續有可能有無窮迴圈的問題(停不下來)
            if session["user"]["isFinishedQuestions"][session["user"]["preStep"]] == False: # 前一次沒問完 return 前一次繼續問 
                return session["user"]["preStep"]
            else: # 前一次問完了 return 找 steps 的下一個 
                for step in session["user"]["steps"]:
                    if session["user"]["isFinishedQuestions"][step] == False:
                        return step
        else:
            if session["user"]["isFinishedQuestions"][session["user"]["preStep"]] == False: # 前一次沒問完 return 前一次繼續問 
                return session["user"]["preStep"]
            else: # 前一次問完了
                if session["user"]["isFinishedQuestions"][nowQ] == False: # 這次偵測到的問題還沒問完 繼續問
                    return nowQ
                else: # 這次偵測到的問題已經問完了 => 從 steps 中找下一個
                    for step in session["user"]["steps"]:
                        if session["user"]["isFinishedQuestions"][step] == False:
                            return step
                        
def detectSymptom(inputSentence):
    
    symptomsList = [ [] for _ in range(6)]
    for symptomTypeId in range(len(symptomTypeKeywords)):
        for symptom in symptomTypeKeywords[symptomTypeId]:
            if symptom in inputSentence and symptom not in symptomsList[symptomTypeId]:
                symptomsList[symptomTypeId].append(symptom)
            if symptom in inputSentence and symptom not in session["user"]["potentialSymptoms"][symptomTypeId]:
                session["user"]["potentialSymptoms"][symptomTypeId].append(symptom)
    return symptomsList

def detectEvent(inputSentence):
    for index in range(len(eventTypeKeywords)):
        for event in eventTypeKeywords[index]:
            if event in inputSentence:
                return index
    return None

def getNewUserInfo(account , tts , stt):

    steps = sorted(["q" + str(i) for i in range(1,12)],key= lambda k : random.random())
    steps.pop(steps.index("q4"))
    steps.pop(steps.index("q6"))
    steps.insert(0,"q4")
    steps.append("q6")
    steps.append("end")

    return { 
             "account" : account,
             "tts" : tts,
             "stt" : stt,
             "isFinishedQuestions" : {"event1" : False, "event2" : False , "event3" : False ,"chit":False, "q1":False,"q2":False,"q3":False,"q4":False,"q5":False,"q6":False,"q7":False,"q8":False,"q9":False,"q10":False,"q11":False,"end":False},
             "askingTimes" : {"event1" : 1 ,"event2": 1,"event3": 1,"chit" : 1 ,"q1": 2 ,"q2": 2 ,"q3": 2 ,"q4": 2 ,"q5": 2 ,"q6": 2 ,"q7": 1 ,"q8": 1 ,"q9": 1 ,"q10": 1 ,"q11": 1 ,"end": 1 },
             "potentialSymptoms" : [ [] for _ in range(6) ],
             "potentialEvents" : [],
             "steps" : steps,
             "preStep" : "chit",
             "nowTimes" : 1
            }
    
def validLogin(account, password):
    if account == "123" and password == "123":
        return True
    else: 
        False

def getPreStepWord(preStep):
    if preStep == "q1":
        return "對於睡眠的問題，請以拉霸的方式來表示你對於這個問題的嚴重程度。"
    elif preStep == "q2":
        return "對於緊張不安的問題，請以拉霸的方式來表示你對於這個問題的嚴重程度。"
    elif preStep == "q3":
        return "對於苦惱或動怒的問題，請以拉霸的方式來表示你對於這個問題的嚴重程度。"
    elif preStep == "q4":
        return "對於憂鬱心情低落的問題，請以拉霸的方式來表示你對於這個問題的嚴重程度。"
    elif preStep == "q5":
        return "對於比不上別人的問題，請以拉霸的方式來表示你對於這個問題的嚴重程度。"
    elif preStep == "q6":
        return "對於自殺念頭的問題，請以拉霸的方式來表示你對於這個問題的嚴重程度。"

def getReply(account, sessionTts, reply, popup = "0", preStepWord = ""):

    dirPath = f"./static/tts/{account}"
    if sessionTts == "0":
        return  {
        "isUser": False,
        "isText": True,
        "reply": reply,
        "ttsPath": "",
        "popup": popup ,
        "preStep": preStepWord
        }
    elif sessionTts == "1":
        tts_client = hts_synthesis_client.TTSCrossLanguage()
        tts_client.set_language(language="zh",speaker="UDN")
        ttsPath = tts_client.askForService(text = reply, dir_path= dirPath, file_name = datetime.now().strftime("%H%M%S") + ".wav")
        return  {
        "isUser": False,
        "isText": True,
        "reply": reply,
        "ttsPath" : ttsPath,
        "popup": popup ,
        "preStep": preStepWord
        }
    elif sessionTts == "2":
        tts_client = hts_synthesis_client.TTSClient()
        tts_client.set_language(language="taiwanese_sandhi", model="M12")
        ttsPath = tts_client.askForService(data = reply, dir_path= dirPath , file_name = datetime.now().strftime("%H%M%S") + ".wav") 
        return  {
        "isUser": False,
        "isText": True,
        "reply": reply,
        "ttsPath" : ttsPath,
        "popup": popup,
        "preStep": preStepWord
        }


def clearCacheFile():
    
    try: # clear tts
        account = session["user"]["account"]
        
        files = glob.glob(f"./static/tts/{account}/*")
        for f in files:
            os.remove(f)
    except Exception as e:
        print(e)
    
    try: # clear stt
        account = session["user"]["account"]
        
        files = glob.glob(f"./static/stt/{account}/*")
        for f in files:
            os.remove(f)
        session.clear()
    except Exception as e:
        print(e)

def scoring(text):
    pass
    

app = Flask(__name__,
        static_folder="static", # 放置靜態物件的名稱
        static_url_path="/static",)

CORS(app)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=10)
app.config['UPLOAD_FOLDER'] = "./static/stt"
app.secret_key = os.urandom(24)



@app.route('/', methods = ["GET","POST"])
def login():
    if request.method == "GET":
        clearCacheFile()
        return render_template('login.html')
    else:
        account = request.form["account"]
        password = request.form["password"]
        stt = request.form["stt"]
        tts = request.form["tts"]
        success = validLogin(account,password)
        if success:
            session["user"] = getNewUserInfo(account,tts,stt)
            return redirect(url_for("chatbot"),code=307) 
        else:
            return render_template('login.html')
        

@app.route('/chatbot' , methods = ["POST"])
def chatbot():
    return render_template('index.html')

@app.route('/upload',  methods=['POST'])
def upload_data():
    data = request.get_json()
    with open("user.txt","a+",encoding="utf-8") as f:
        f.write(str(data['message_list']))
        f.write("\n")  
    return "ok"

@app.route('/thank')
def thank():
    clearCacheFile()
    return render_template("thank.html")

@app.route("/result", methods=["POST"])
def result():

    account = session["user"]["account"]
    stt = session["user"]["stt"]
    if stt == "0":
        return ""
    dirPath = f"./static/stt/{account}"
    if not os.path.isdir(dirPath):
        os.mkdir(dirPath)
    audio_blob = request.files['data'] # <class 'werkzeug.datastructures.FileStorage'>

    # TODO: is there any way to avoid saving wav file and read them again?
    fname = str(time.time())[:14]
    with open(f"{dirPath}/{fname}.webm", "wb") as _f:
        audio_blob.save(_f)
    
    os.system(f"ffmpeg -loglevel error -y -i {dirPath}/{fname}.webm -ar 16000 -ac 1 {dirPath}/{fname}.wav")
    time.sleep(0.5)
    filePath = f"{dirPath}/{fname}.wav"
    if stt == "1":
        text = asr.stt_chinese(filePath)
        return jsonify({"stt" : text})
    elif stt == "2":
        text = asr.stt_taiwanese(filePath)
        return jsonify({"stt" : text})

    return ""
 

@app.route('/getReply', methods=['POST'])
def query_news():

    data = request.get_json()
    userInput = data["input_message"]   
    if userInput == "":
        return  getReply(session["user"]["account"], session["user"]["tts"], "請輸入文字")
    userCkip = json.loads(req.post("http://140.116.245.157:2001", data={"data":userInput, "token":TOKEN}).text) # json 格式
    # print("preStep: " + str(session["user"]["preStep"]))
    if session["user"]["nowTimes"] == session["user"]["askingTimes"][session["user"]["preStep"]]:
        session["user"]["nowTimes"] = 0
        session["user"]["isFinishedQuestions"][session["user"]["preStep"]] = True  
    nowQuestion = detectSentenceType(userCkip["ws"][0])
    eventId = detectEvent(userInput)
    # print("eventId: " + str(eventId))
    if eventId != None and (session["user"]["isFinishedQuestions"]["event1"] == False or session["user"]["isFinishedQuestions"]["event2"] == False or session["user"]["isFinishedQuestions"]["event3"] == False):
        if session["user"]["isFinishedQuestions"]["event1"] == False:
            session["user"]["potentialEvents"].append(eventId)
            nowQuestion = "event1"
        elif session["user"]["isFinishedQuestions"]["event2"] == False and eventId not in session["user"]["potentialEvents"]:
            session["user"]["potentialEvents"].append(eventId)
            nowQuestion = "event2"
        elif session["user"]["isFinishedQuestions"]["event3"] == False and eventId not in session["user"]["potentialEvents"]:
            session["user"]["potentialEvents"].append(eventId)
            nowQuestion = "event3"

    if nowQuestion.startswith("event"):
        session["user"]["isFinishedQuestions"]["event" + nowQuestion[-1]] = True
        session.modified = True
        return getReply(session["user"]["account"], session["user"]["tts"], eventSentences[eventId][0])
    
    
    if nowQuestion == "end":
        session["user"]["isFinishedQuestions"]["end"] = True
        session.modified = True
        return getReply(session["user"]["account"], session["user"]["tts"], othersSentences[2][0])
    
    # print("nowQuestion: " + str(nowQuestion))

    symptomsList = detectSymptom(userInput)
    # print("symptomsList: " + str(symptomsList))

    basicSentencesId = int(nowQuestion[1:])-1
    # print("basicSentencesId: " + str(basicSentencesId + 1))

    if session["user"]["isFinishedQuestions"][session["user"]["preStep"]]:
        session["user"]["nowTimes"] += 1
        preStepWord = getPreStepWord(session["user"]["preStep"])
        ps = session["user"]["preStep"]
        # print("nowTimes: " + str(session["user"]["nowTimes"]))
        session["user"]["preStep"] = nowQuestion
        session.modified = True
        # print(session.get("user"))
        # print("isFinishedQuestions: " + str(session["user"]["isFinishedQuestions"]))
        # print("================= IF =======================")
        if ps == "q1" or ps == "q2" or ps == "q3" or ps == "q4" or ps == "q5" or ps == "q6":
            return getReply(session["user"]["account"], session["user"]["tts"], replyWords[random.randint(0,len(replyWords)-1)] + basicSentences[basicSentencesId][random.randint(0,3)],"1",preStepWord)
        else:
            return getReply(session["user"]["account"], session["user"]["tts"], replyWords[random.randint(0,len(replyWords)-1)] + basicSentences[basicSentencesId][random.randint(0,3)])
    
    else:
        if session["user"]["nowTimes"] == 1:
            session["user"]["nowTimes"] += 1
            # print("nowTimes: " + str(session["user"]["nowTimes"]))
            session["user"]["preStep"] = nowQuestion
            session.modified = True
            # print(session.get("user"))
            # print("isFinishedQuestions: " + str(session["user"]["isFinishedQuestions"]))
            # print("==================ELSE IF======================")
            return getReply(session["user"]["account"], session["user"]["tts"], intensitySentences[basicSentencesId][0])

        else:
            session["user"]["nowTimes"] += 1
            # print("nowTimes: " + str(session["user"]["nowTimes"]))
            session["user"]["preStep"] = nowQuestion
            session.modified = True
            # print(session.get("user"))
            # print("isFinishedQuestions: " + str(session["user"]["isFinishedQuestions"]))
            return getReply(session["user"]["account"], session["user"]["tts"], replyWords[random.randint(0,len(replyWords))] + basicSentences[basicSentencesId][random.randint(0,3)])
    
            

if __name__ == '__main__':

    app.run(host='127.0.0.1', port='8888', debug=True, ssl_context='adhoc')
    
    


