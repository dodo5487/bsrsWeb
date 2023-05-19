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

symptomKeywordsList = [['寢食難安', '健忘', '記憶混亂', '記憶困難', '記憶力變差', '記憶力減退', '注意力渙散', '精神疲乏', '失眠', '晚睡', '多眠', '早醒', '無法入睡', '嗜睡', '睡的少'],
                       ['不安', '不踏實', '不寒而慄', '掙脫不了', '想逃', '緊張兮兮', '膽怯', '瘋狂', '膽戰心驚', '發怵', '害怕', '驚嚇', '恐怖', '恐懼', '受驚', '心有餘悸', '羞愧', '慚愧', '丟臉', '丟人', '害羞', '可恥', '虧心', '愧疚', '難堪', '難看', '怕羞', '羞恥', '羞辱', '無所適從', '衝動', '激動', '緊張', '惶惑', '驚駭', '驚恐', '懼怕', '畏懼', '畏怯', '心驚膽戰', '心驚肉跳', '毛咕', '毛骨悚然', '失色', '失魂落魄', '生怕', '生恐', '屁滾尿流', '忌憚', '怯場', '杯弓蛇影', '畏縮', '風聲鶴唳', '望而生畏', '喪膽', '惶恐', '惶惶', '提心吊膽', '猶有餘悸', '發毛', '虛驚', '聞風喪膽', '魂不附體', '魂飛魄散', '談虎色變', '戰戰兢兢', '擔驚受怕', '懸心弔膽', '懸心吊膽', '懼色', '驚愕', '驚惶', '驚惶失措', '驚慌', '驚慌失措', '驚魂', '驚魂不定', '卑怯', '怯生', '怯生生', '怯弱', '怯懦', '怕生', '柔弱', '畏首畏尾', '畏葸', '畏葸不前', '苟且偷生', '苟且偷安', '脆弱', '婆婆媽媽', '貪生怕死', '軟弱', '愚懦', '懦弱', '縮手縮腳', '縮頭縮腳', '膽小', '膽小如鼠', '膽小怕事', '膽寒', '膽虛', '薄弱', '可怖', '可怕', '駭人聽聞', '嚇人', '嚇死', '觸目驚心', '入魔', '耿耿', '做賊心虛', '庸人自擾', '掛心', '掛慮', '牽心', '惴惴不安', '惶惶不安', '揪心', '焦慮不安', '焦慮', '駭異', '駭然', '戒心', '惕厲', '警戒', '鑑戒', '半信半疑', '生疑', '多心', '多疑', '存疑', '狐疑', '起疑', '將信將疑', '猜疑', '置疑', '疑心', '疑神疑鬼', '疑問', '質疑', '闕疑'],
                       ['不快', '不爽', '不平', '不忿', '不順心', '不耐煩', '不滿', '不知所措', '自作自受', '心浮氣躁', '不要煩我', '任性', '真煩', '很煩', '煩人', '馬的', '媽的', '靠北', '哭霸', '哭爸', '哭腰', '靠腰', '哭么', '靠么', '發脾氣', '飆髒話', '討厭鬼', '怒罵', '責備', '打擊', '罵', '一肚子火', '王八蛋', '死不完', '你他媽', '我他媽', '他媽的', '他馬的', '操你媽', '操他媽', '去你媽', '幹你娘', '幹恁娘', '幹拎娘', '幹您娘', '幹林娘', '乾林良', '沈重', '辛苦', '有病', '煩死', '心煩氣躁', '自以為是', '憤慨', '憤怒', '惱火', '氣不過', '氣不忿', '氣憤', '痛苦', '無所謂', '怨恨', '仇恨', '敵視', '敵意', '妒忌', '嫉妒', '反感', '可恨', '可惡', '厭惡', '憎恨', '受傷', '煩悶', '難受', '心煩', '厭煩', '冷血', '著急', '浮躁', '急切', '急躁', '焦急', '焦慮', '心急', '心急如焚', '心切', '心慌', '發慌', '恐慌', '心慌意亂', '懊悔', '悔悟', '懺悔', '後悔', '抱歉', '過意不去', '自私', '急促', '感傷', '內疚', '吃驚', '驚訝', '震驚', '警惕', '疑惑', '懷疑', '可疑', '困惑', '迷茫', '為難', '狂亂', '氣急敗壞', '無奈', '心虛', '煩躁', '苦悶', '苦惱', '納悶', '厭倦', '憤激', '惱怒', '激憤', '氣惱', '盛怒', '悻悻', '震怒', '抱恨', '可憎', '痛恨', '痛惡', '嫌怨', '嫌惡', '嫌隙', '嫌憎', '憎惡', '焦心', '焦躁', '焦灼', '情急', '心焦', '煩亂', '祈求', '紛擾', '如坐針氈', '抱愧', '害臊', '愧恨', '悔恨', '失悔', '痛悔', '追悔', '自怨自艾', '負疚', '歉疚', '詫異', '愕然', '怪訝', '駭怪', '驚詫', '驚異', '迷惑', '迷惘', '彷徨', '疑忌', '哀憐', '憐憫', '憐惜', '痛惜', '掛念', '牽腸掛肚', '眷眷', '眷戀', '渴慕', '貪戀', '鄙視', '鄙夷', '侮蔑', '失意', '懊喪', '抱憾', '悵悵', '惆悵', '落魄', '惘然', '孤寂', '落寞', '落莫', '消魂', '銷魂', '哀思', '哀怨', '悲憤', '悲鬱', '悵恨', '悵惘', '愁苦', '仇怨', '憤恨', '憤懣', '感憤', '戒懼', '驚疑', '敬畏', '愧痛', '悶倦', '惱恨', '惱人', '危懼', '畏忌', '銜恨', '羞憤', '疑懼', '疑慮', '憂煩', '憂憤', '憂懼', '憂悶', '怨憤', '厭棄', '解恨', '發飆', '七竅生煙', '上火', '大發雷霆', '心頭火起', '火冒三丈', '令人髮指', '生氣', '光火', '腦羞成怒', '含怒', '狂怒', '冒火', '勃然大怒', '怒不可遏', '怒沖沖', '怒髮衝冠', '面有慍色', '氣沖沖', '氣呼呼', '動火', '動肝火', '動怒', '動氣', '悻悻然', '悻然', '掛火', '掛氣', '發怒', '發狠', '感忿', '惹氣', '慍怒', '義憤填膺', '嗔怒', '憤然', '憤憤', '暴跳如雷', '激怒', '觸怒', '怏怏', '怨聲載道', '仇隙', '切骨之仇', '民怨', '夙嫌', '幽怨', '怨毒', '怨氣', '冤仇', '恩怨', '宿怨', '深仇大恨', '惡意', '惡感', '悶氣', '睚眥之怨', '敵愾', '積怨', '切齒痛恨', '含恨', '抱恨終身', '咬牙切齒', '怨尤', '怨艾', '怨望', '恨入骨髓', '恨之入骨', '記恨', '恚恨', '積掰', '機掰', '雞掰', '深惡痛絕', '飲恨', '嫉恨', '閉嘴', '懷恨', '臭嘴', '吃醋', '報應', '打嘴砲', '拍馬屁', '妒火中燒', '死八婆', '忌克', '忌妒', '倒楣', '忌刻', '忌恨', '眼紅', '嫉賢妒能', '討嫌', '絮煩', '該死', '作嘔', '嫌棄', '膩味', '膩煩', '心焦如焚', '火燒火燎', '抓耳撓腮', '性急', '急赤白臉', '起急', '干急', '乾瞪眼', '發急', '搓手頓腳', '毛躁', '坐立不安', '急性子', '狷急', '粗暴', '暴躁', '褊急', '操之過急', '操切', '手忙腳亂', '手足無措', '失措', '周章', '倉皇', '倉皇失措', '張皇', '著慌', '慌神', '慌張', '慌亂', '羞赧', '羞慚', '赧然', '赧顏', '腆然', '腆顏', '仗勢欺人', '吐剛茹柔', '污辱', '作踐', '折辱', '侮辱', '玷污', '玷辱', '虐待', '凌虐', '凌辱', '凌轢', '辱沒', '欺人太甚', '欺生', '欺侮', '欺負', '欺凌', '欺壓', '摧殘', '輕侮', '踐踏', '蹂躪', '糟蹋', '褻瀆', '找事', '找茬', '找碴', '過不去', '難為', '利用', '陷害', '公憤', '民憤', '私憤', '幽憤', '義憤', '鬱憤'],
                       ['幹', '不開心', '不高興', '不快樂', '不值得', '不是味兒', '不是滋味', '強顏歡笑', '對不起', '沒心', '捨不得', '膚淺', '爛透', '承受不了', '承受不住', '受不了', '受不瞭', '受不暸', '受不鳥', '喘不過氣', '莫名', '假面', '受夠', '哭訴', '空虛', '空洞', '很糟', '唉', '挫折', '煎熬', '失控', '做不到', '熬不住', '自己扛', '蠢爆了', '離我遠去', '好傻', '很傻', '一無所有', '無言以對', '無言', '走投無路', '走頭無路', '無路可走', '冷嘲熱諷', '幸災樂禍', '遍體麟傷', '悲從中來', '假惺惺', '自以為', '諷刺', '殘忍', '拿走', '折磨', '悲哀', '悲傷', '沉痛', '傷感', '傷心', '痛心', '心酸', '討厭', '窩囊', '憂愁', '擔心', '擔憂', '發愁', '犯愁', '憂慮', '壓抑', '鬱悶', '自卑', '無能感', '委屈', '抱屈', '冤枉', '可憐', '假裝', '困住', '可惜', '惋惜', '心疼', '思念', '懷念', '牽掛', '想念', '輕蔑', '藐視', '蔑視', '輕視', '失望', '悲觀', '沮喪', '茫然', '失落', '失落感', '不知不覺', '奢望', '無望', '心寒', '孤獨', '孤單', '孤立', '寂寞', '低落', '低沉', '消沉', '心灰意懶', '心灰意冷', '沉重', '沉甸甸', '無聊', '沉思', '解氣', '惱羞成怒', '不切實際', '袖手旁觀', '氣餒', '消氣', '喪氣', '掃興', '洩勁', '悲苦', '悲酸', '悲辛', '哀傷', '哀戚', '哀痛', '悲愴', '慘苦', '苦澀', '淒慘', '傷神', '酸楚', '痛心疾首', '辛酸', '誠惶誠恐', '寒心', '熬心', '懊惱', '憋悶', '憋氣', '煩擾', '糟心', '愁悶', '窮愁', '殷憂', '沉鬱', '陰鬱', '索然無味', '黯淡', '暗淡', '頹廢', '頹靡', '頹喪', '頹唐', '委靡', '彆扭', '遺憾', '心如刀割', '生不如死', '如喪考妣', '肝腸寸斷', '兔死狐悲', '哀哀', '哀毀骨立', '苦痛', '絕不', '淒切', '淒涼', '淒惻', '淒愴', '悲切', '悲慼', '悲痛', '悲愁', '悲慟', '悲慟不已', '破碎', '椎心', '椎心泣血', '痛不欲生', '痛切', '痛定思痛', '傷心欲絕', '無助', '傷悲', '傷痛', '腸斷', '慘然', '慘痛', '酸辛', '樂極生悲', '斷腸', '難過', '亡魂喪膽', '大驚失色', '沉悶', '悶悶不樂', '悶悶的', '悶悶', '愁眉苦臉', '煩惱', '窩愁', '鬱悒', '鬱悒寡歡', '鬱鬱寡歡', '人心惶惶', '六神無主', '日坐愁城', '多愁善感', '作賊心虛', '杞人憂天', '芒刺在背', '忐忑', '哀愁', '愁腸百結', '憂心', '憂心如焚', '憂心忡忡', '憂悒', '憂戚', '憂憤成疾', '憂鬱成疾', '懸心', '顧慮', '鬱結', '鬱積', '束縛', '牢籠', '拘謹', '拘束', '枷鎖', '桎梏', '強壓', '牽制', '牽掣', '壓制', '檢束', '關礙', '自抑', '自製', '自持', '克制', '忍受', '忍耐', '忍氣吞聲', '按捺', '容忍', '隱忍', '叫屈', '含屈而終', '受屈', '抱屈含冤', '暗暗叫屈', '窩氣', '自悔', '悔不當初', '悔之已晚', '悔之無及', '追悔莫及', '嗟悔', '愧悔', '噬臍莫及', '翻悔', '悔改', '悔罪', '悔過', '覺悟', '同病相憐', '其情可憫', '哀矜', '肉痛', '歎惋', '念念不忘', '念舊', '思鄉', '思慕', '思親', '相思', '記掛', '惦念', '惦記', '牽念', '眷念', '朝思暮想', '渴想', '軫念', '感念', '感懷', '懷古', '懷想', '懷舊', '懷戀', '顧念', '向隅', '死心', '事與願違', '垂頭喪氣', '絕望', '萬念俱灰', '廢然', '心如死灰', '意懶心灰', '厭世', '聽天由命', '一籌莫展', '力不從心', '心有餘而力不足', '心餘力絀', '巧婦難為無米之炊', '坐以待斃', '束手待斃', '束手無策', '沒奈何', '沒門兒', '沒轍', '奈何', '孤掌難鳴', '怎奈', '迫不得已', '望洋興歎', '存亡', '懶散', '沒路用', '無可奈何', '無計可施', '無能為力', '無能', '傷口', '愛莫能助', '萬不得已', '萬般無奈', '遠水救不了近火', '獨木不成林', '獨木難支', '黔驢技窮', '鞭長莫及', '人情淡薄', '世態炎涼', '冰冷', '冷冰冰', '冷言冷語', '冷若冰霜', '冷淡', '冷漠', '冷漠無情', '冷酷', '冷酷無情', '神情淡漠', '淡薄', '無動於衷', '無情', '漠不關心', '漠然置之', '沖沖', '怒氣沖沖', '灰心', '灰溜溜', '沒精打采', '洩氣', '氣短', '消極', '得過且過', '敗興', '被動', '無精打采', '萎靡', '傷氣', '意志消沉', '意興闌珊', '槁木死灰', '頹然', '懨懨', '黯然', '黯然神傷', '沉濁', '深沉', '悶沉沉', '悶聲悶氣', '濃濁', '迷漫', '漠漠', '漫天', '瀰漫', '靉靆', '入骨', '沉沉', '刻骨', '徹骨', '烏雲密佈', '陰暗', '陰冷', '陰沉', '陰霾', '汍瀾', '吞聲', '呼天搶地', '抽泣', '抽咽', '泣不成聲', '泫然', '哀泣', '哀號', '淚', '流淚', '哭天抹淚', '哭泣', '哭哭啼啼', '哭鼻子', '哭嚎', '哽咽', '唏噓', '涕泣', '涕泗滂沱', '涕淚俱下', '鬼哭狼嚎', '乾號', '啜泣', '淚水', '淚如雨下', '淚如泉湧', '淚汪汪', '淚花', '淚流滿面', '淚珠', '淚液', '眼淚', '掉眼淚', '啼泣', '啼哭', '悲泣', '悲咽', '悲哽', '揮淚', '痛哭', '痛哭流涕', '飲泣', '嗚咽', '號哭', '慟哭', '漣洏', '漣漣', '撲簌', '撕心裂肺', '潸然', '潸潸', '熱淚盈眶', '嚎啕', '嚎啕大哭', '簌簌', '聲淚俱下', '灑淚', '心病', '鄉愁', '愁思', '愁腸', '愁緒', '憂思', '隱憂', '離愁', '打馬虎眼', '悵然', '惘然若失', '惝怳', '惝恍', '由不得', '忍不住', '忍無可忍', '抒情', '抒發', '宣洩', '洩恨', '洩憤', '發抒', '發洩', '禁不住', '禁不起', '縱情', '難忍', '難耐', '灰暗', '昏天黑地', '昏沉', '昏黑', '昏暗', '幽幽', '幽暗', '暗淡無光', '慘淡', '心情不好'],
                       ['不懂', '不詳', '不值一提', '不屑', '不屑一顧', '不堪一擊', '不起眼', '配不上', '拖累', '羞怯', '憂傷', '淡漠', '漠然', '漠視', '自慚形穢', '自餒', '自滿', '自恃', '無地自容', '羞人', '羞澀', '妄自菲薄', '自愧弗如', '自慚', '自輕自賤', '自暴自棄', '一事無成', '小看', '小視', '小瞧', '白眼', '歧視', '看不起', '看輕', '無足輕重', '背叛', '無視', '菲薄', '視如糞土', '讓步', '睇小', '嗤之以鼻', '微不足道', '睥睨', '鄙棄', '鄙薄', '賤視', '瞧不起', '差強人意', '隨便', '如饑似渴', '大失所望', '自欺欺人', '命運', '噩夢', '失敗', '累贅', '放棄', '犧牲', '頂嘴', '多餘'],
                       ['想不開', '勒死', '掛掉', '自殺', '跳樓', '跳海', '上吊', '尋死', '輕生', '消失', '往生', '永別', '遺物', '生死', '天堂', '結束', '燒炭', '割腕', '做傻事', '想死', '尋短', '解脫', '不想活']
                       ]

eventsList = ['不想出門', '不想上班', '不想說話', '不想講話', '不想看醫生', '不想回家', '不想上學', '不想回去', '不想吃飯', '不想讀書', '不想上課', '不想起床', '不想念書', '不想工作', '不想要出門', '不想要念書', '不想吃藥', '不想吃東西', '不想接觸人群', '不想找工作', '不想做事', '不想要吃藥', '不想看電視', '不想接電話', '不想跟人說話', '不想跟人相處', '不想跟人講話', '不想跟人聊天', '不想跟人交談', '不想跟人互動', '不想跟人出去', '課業的問題', '論文做不完', '學校的問題', '錢的負擔', '小孩的問題', '課業的事情', '課業的壓力', '異樣的眼光', '現實的落差', '父母的壓力', '高壓的狀態', '機車的老闆娘', '錢的問題', '被誤會', '被放鳥', '被狂操', '被死釘', '搞我', '傷害我', '騙我', '拋棄我', '推開我', '跟蹤我', '嘲諷我', '惹到我', '揶揄我', '圍剿我', '壓迫我', '凌虐我', '數落我', '不理我', '住院', '休學', '分手', '吵架', '辭職', '離婚', '離家', '熬夜', '爭吵', '作弊', '絕交', '經濟壓力', '工作噩夢', '愛恨情仇', '混蛋客人', '論文壓力', '酒鬼父親', '財務問題', '課業因素', '功課壓力', '腦殘老闆', '情愛糾葛', '課業問題', '身材問題', '社會現實', '鳥事', '感情犧牲品', '煩惱論文', '爸媽面子', '無法承受', '無法溝通', '無法錄取', '無法挽回', '對我說謊', '讓我哭', '對我發脾氣', '對我說教', '被拋棄', '被罵', '被打', '被欺負', '被開除', '被整死', '被傷害', '被念', '被騙', '被遺棄', '被羞辱', '被嘲弄', '給趕走', '被排斥', '被排擠', '被虐待', ',被吵醒', '受欺負', '被當掉', '被背叛', '被丟下', '被侷限', '被折騰', '受摧殘', '被強暴', '被恥笑', '被剝奪', '受折磨', '被壓抑', '被束縛', '被踐踏', '被綁死', '閱讀障礙', '接近人群', '做錯事情', '丟工作', '吊點滴', '辦不了貸款', '放棄論文', '拿掉孩子', '劈腿', '發病', '復發', '離職', '遲到', '發酒瘋', '酗酒', '失戀', '心碎', '心寒', '無家可歸', '肄業', '失業', '失調', '自作多情', '沒錢', '沒收入', '沒安全感', '沒朋友', '沒人緣', '沒有社交', '病情', '惡夢', '醫藥費', '完美主義', '重考', '閒言閒語', '家暴', '第三者']

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
                        
def detectSymptom(text,preStep):
    if preStep in ["q1","q2","q3","q4","q5","q6"]:
        index = int(preStep[-1]) - 1
        for symptom in symptomKeywordsList[index]:
            if symptom in text and symptom not in session["user"]["potentialSymptoms"][index]:
                print(symptom)
                session["user"]["potentialSymptoms"][index].append(symptom)
                session.modified = True
            
def detectEvent(text):
    for event in eventsList:
        if event in text and event not in session["user"]["potentialEvents"]:
            print(event)
            session["user"]["potentialEvents"].append(event)
            session.modified = True


def detectEventType(inputSentence):
    for index in range(len(eventTypeKeywords)):
        for event in eventTypeKeywords[index]:
            if event in inputSentence:
                return index
    return None

def getNewUserInfo(account , tts , stt): # new user's session setting

    steps = sorted(["q" + str(i) for i in range(1,12)],key= lambda k : random.random())
    steps.pop(steps.index("q4"))
    steps.pop(steps.index("q6"))
    steps.insert(0,"q4")
    steps.append("q6")
    steps.append("end")
    score = [-1 for _ in range(6)]

    return { 
             "account" : account,
             "tts" : tts,
             "stt" : stt,
             "isFinishedQuestions" : {"event1" : False, "event2" : False , "event3" : False ,"chit":False, "q1":False,"q2":False,"q3":False,"q4":False,"q5":False,"q6":False,"q7":False,"q8":False,"q9":False,"q10":False,"q11":False,"end":False},
             "askingTimes" : {"event1" : 1 ,"event2": 1,"event3": 1,"chit" : 1 ,"q1": 2 ,"q2": 2 ,"q3": 2 ,"q4": 2 ,"q5": 2 ,"q6": 2 ,"q7": 1 ,"q8": 1 ,"q9": 1 ,"q10": 1 ,"q11": 1 ,"end": 1 },
             "potentialSymptoms" : [ [] for _ in range(6) ],
             "potentialEvents" : [],
             "potentialEventsId" : [],
             "steps" : steps,
             "score" : score,
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

def getReply(nowQuestion, lastQuestion, account, sessionTts, reply, popup = "0", preStepWord = ""):

    dirPath = f"./static/tts/{account}"
    if sessionTts == "0":
        return  {
        "isUser": False,
        "isText": True,
        "nowQuestion": nowQuestion,
        "lastQuestion": lastQuestion,
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
        "nowQuestion": nowQuestion,
        "lastQuestion": lastQuestion,
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
        "nowQuestion": nowQuestion,
        "lastQuestion": lastQuestion,
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

def scoring(text): # detect the text's score from 0 to 4
    score = -1
    scoringWords = [
    ["0","沒有","零","零分","0分"],
    ["1","很少","一","一分","1分"],
    ["2","有時候","二","兩分","二分","2分"],
    ["3","經常","三","三分","3分"],
    ["4","幾乎每天","四","四分","4分"]]
    for i in range(len(scoringWords)):
        for j in range(len(scoringWords[i])):
            if scoringWords[i][j] in text:
                return i
            
    # TODO : 考慮到多種回答的情況
    return score

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

@app.route('/feedback' , methods = ["POST"])
def feedback():
    return "ok"

@app.route('/upload',  methods=['POST'])
def upload_data():
    data = request.get_json()
    with open("user.txt","a+",encoding="utf-8") as f:
        f.write(str(data['message_list']))
        f.write("\n")  
    return "ok"

@app.route('/thank')
def thank():
    summarySentencesList = [
        "您的情緒狀況屬於正常範圍，表示身心適應狀況良好。",
        "您屬於輕度情緒困擾，建議做好壓力管理, 找家人或朋友談談，抒發心情。",
        "看起來您最近壓力指數有點高，屬於中度情緒困擾，建議尋求並接受心理專業諮詢。",
        "看起來您最近壓力指數有點高，屬於重度情緒困擾，需要高度關懷，建議尋求專業輔導或精神科診療。",
        "看起來您最近壓力指數有點高，建議尋求專業輔導或精神科治療。"
        ]
    # clearCacheFile()
    scoreList = session["user"]["score"]
    q6Score = int(scoreList[5])
    score = 0
    events = session["user"]["potentialEvents"]
    symptoms = session["user"]["potentialSymptoms"]
    for i in range(5):
        score += int(scoreList[i])
    
    if q6Score >= 2:
        summary = {"q6Score":q6Score, "score": score, "summaryText":summarySentencesList[4], "events":events, "symptoms":symptoms}
    elif score <= 5:
        summary = {"q6Score":q6Score, "score": score, "summaryText":summarySentencesList[0], "events":events, "symptoms":symptoms}
    elif score >=6 and score <=9:
        summary = {"q6Score":q6Score, "score": score, "summaryText":summarySentencesList[1], "events":events, "symptoms":symptoms}
    elif score >=10 and score <=14:
        summary = {"q6Score":q6Score, "score": score, "summaryText":summarySentencesList[2], "events":events, "symptoms":symptoms}
    elif score >=15:
        summary = {"q6Score":q6Score, "score": score, "summaryText":summarySentencesList[3], "events":events, "symptoms":symptoms}
    
    return render_template("thank.html" , summary = summary)

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
 
@app.route('/getSliderValue', methods=['POST'])
def getSliderValue():
    data = request.get_json()
    sliderValue = data["sliderValue"]
    lastQuestionIndex = int(data["lastQuestion"][-1])
    # print("lastQuestionIndex: " + str(lastQuestionIndex))
    # print("sliderValue: " + str(sliderValue))
    session["user"]["score"][lastQuestionIndex - 1] = sliderValue
    session.modified = True
    return "ok"

@app.route('/getReply', methods=['POST'])
def query_news():

    data = request.get_json()
    userInput = data["input_message"]  
    if userInput == "":
        return  getReply(None, None, session["user"]["account"], session["user"]["tts"], "請輸入文字")
    userCkip = json.loads(req.post("http://140.116.245.157:2001", data={"data":userInput, "token":TOKEN}).text) # json 格式
    # print("preStep: " + str(session["user"]["preStep"]))
    if session["user"]["nowTimes"] == session["user"]["askingTimes"][session["user"]["preStep"]]:
        session["user"]["nowTimes"] = 0
        session["user"]["isFinishedQuestions"][session["user"]["preStep"]] = True  
    nowQuestion = detectSentenceType(userCkip["ws"][0])
    eventId = detectEventType(userInput)

    detectSymptom(userInput,session['user']['preStep']) 
    detectEvent(userInput)
    # print("eventId: " + str(eventId))
    if eventId != None and (session["user"]["isFinishedQuestions"]["event1"] == False or session["user"]["isFinishedQuestions"]["event2"] == False or session["user"]["isFinishedQuestions"]["event3"] == False):
        if session["user"]["isFinishedQuestions"]["event1"] == False:
            session["user"]["potentialEventsId"].append(eventId)
            nowQuestion = "event1"
        elif session["user"]["isFinishedQuestions"]["event2"] == False and eventId not in session["user"]["potentialEventsId"]:
            session["user"]["potentialEventsId"].append(eventId)
            nowQuestion = "event2"
        elif session["user"]["isFinishedQuestions"]["event3"] == False and eventId not in session["user"]["potentialEventsId"]:
            session["user"]["potentialEventsId"].append(eventId)
            nowQuestion = "event3"

    if nowQuestion.startswith("event"):
        session["user"]["isFinishedQuestions"]["event" + nowQuestion[-1]] = True
        session.modified = True
        return getReply("event" + nowQuestion[-1], session["user"]["preStep"] ,session["user"]["account"], session["user"]["tts"], eventSentences[eventId][0])
    
    
    if nowQuestion == "end":
        session["user"]["isFinishedQuestions"]["end"] = True
        session.modified = True
        preStepWord = getPreStepWord(session["user"]["preStep"])
        ps = session["user"]["preStep"]
        if ps == "q1" or ps == "q2" or ps == "q3" or ps == "q4" or ps == "q5" or ps == "q6":
            return getReply("end", ps, session["user"]["account"], session["user"]["tts"], othersSentences[2][0] ,"1", preStepWord)
        else:
            return getReply("end", session["user"]["preStep"], session["user"]["account"], session["user"]["tts"], othersSentences[2][0])
    
    # print("nowQuestion: " + str(nowQuestion))


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
            return getReply(nowQuestion, ps, session["user"]["account"], session["user"]["tts"], replyWords[random.randint(0,len(replyWords)-1)] + basicSentences[basicSentencesId][random.randint(0,3)],"1",preStepWord)
        else:
            return getReply(nowQuestion, ps, session["user"]["account"], session["user"]["tts"], replyWords[random.randint(0,len(replyWords)-1)] + basicSentences[basicSentencesId][random.randint(0,3)])
    
    else:
        if session["user"]["nowTimes"] == 1:
            session["user"]["nowTimes"] += 1
            ps = session["user"]["preStep"]
            # print("nowTimes: " + str(session["user"]["nowTimes"]))
            session["user"]["preStep"] = nowQuestion
            session.modified = True
            # print(session.get("user"))
            # print("isFinishedQuestions: " + str(session["user"]["isFinishedQuestions"]))
            # print("==================ELSE IF======================")
            return getReply(nowQuestion, ps, session["user"]["account"], session["user"]["tts"], intensitySentences[basicSentencesId][0])

        else:
            session["user"]["nowTimes"] += 1
            ps = session["user"]["preStep"]
            # print("nowTimes: " + str(session["user"]["nowTimes"]))
            session["user"]["preStep"] = nowQuestion
            session.modified = True
            # print(session.get("user"))
            # print("isFinishedQuestions: " + str(session["user"]["isFinishedQuestions"]))
            return getReply(nowQuestion, ps, session["user"]["account"], session["user"]["tts"], replyWords[random.randint(0,len(replyWords))] + basicSentences[basicSentencesId][random.randint(0,3)])
    
            

if __name__ == '__main__':

    app.run(host='127.0.0.1', port='8888', debug=True, ssl_context='adhoc')
    
    


