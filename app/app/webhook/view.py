from flask import Blueprint, request
import requests
import json
from pymongo import MongoClient
from ..config import develop as default_config
from datetime import datetime
import PyICU
import random
from ..brain import function as function

webhook_blueprint = Blueprint('webhook', __name__)
mongo = MongoClient('mongodb://db:27017')

user = mongo.db.users

greeting_dialog = ['สวัสดี','หวัดดี','ทักทาย','Hello','Greeting','ไง','hi']
greeting_ans_dialog_first = ['เมี๊ยว ยินดีที่ได้รู้จักนะคุณ ', 'เมี๊ยว สวัสดีคุณ ', 'เมี๊ยว ดีใจจังที่คุณ ']
greeting_ans_dialog_end = [' เหมียวสามารถช่วยคุณค้นหาโครงการได้นะ', ' เหมียวพร้อมช่วยคุณค้นหาโครงการแล้ว', ' ทักมาให้เหมียวเป็นตัวช่วยในการค้นหาโครงการ']

def send_message(sender_id, message_text):
    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params={
            'access_token': default_config.FB_PAGE_TOKEN
        },
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
                'recipient': {'id': sender_id},
                'message': {'text': message_text}
            }
        )
    )

    # print(r.json)
    return

def sendGeneric(sender_id, message_text):

    messageData = {
        'attachment':{
            'type': 'template',
            'payload': {
                'template_type':'generic',
                'elements':[{
                    'title':'TEST1',
                    'subtitle':'THIS_IS_PAGE_1',
                    'image_url':'',
                    'buttons':[{
                        'type':'web_url',
                        'url':'https://taejai.com/th/projects/all/',
                        'title':'เวปไซต์เทใจ'
                    },{
                        'type':'postback',
                        'title':'ต้องการให้ช่วย',
                        'payload':'ค้นหา'
                    }]
                }]
            }
        }
    }

    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params={
            'access_token': default_config.FB_PAGE_TOKEN
        },
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
                'recipient': {'id': sender_id},
                'message': messageData
            }
        )
    )

    return

def guideline(sender_id, message_text):
    messageData = {
        'attachment':{
            'type': 'template',
            'payload': {
                'template_type':'generic',
                'elements':[{
                    'title':'การใช้งานเบิ้องต้น',
                    'subtitle':'พิมพ์ ค้นหา เพื่อเริ่มต้นการค้นหาโครงการต่างๆ',
                    'image_url':'',
                    'buttons':[{
                        'type':'web_url',
                        'url':'https://taejai.com/th/projects/all/',
                        'title':'เวปไซต์เทใจ'
                    },{
                        'type':'postback',
                        'title':'ค้นหาโครงการ',
                        'payload':'ค้นหา'
                    }]
                }]
            }
        }
    }
    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params={
            'access_token': default_config.FB_PAGE_TOKEN
        },
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
                'recipient': {'id': sender_id},
                'message': messageData
            }
        )
    )
    return

def greeting(sender_id, message_text, doc):

    ranNum = random.randrange(len(greeting_ans_dialog_first))
    text = greeting_ans_dialog_first[ranNum]+doc['sender_name']+ greeting_ans_dialog_end[ranNum]

    messageData = {
        'attachment':{
            'type': 'template',
            'payload': {
                'template_type':'button',
                'text':text,
                    'buttons':[{
                        'type':'postback',
                        'title':'ต้องการให้ช่วย',
                        'payload':'ค้นหา'
                    }]
                }
            }
        }


    greeting_dict = ' เหมียวสามารถช่วยคุณค้นหาโครงการในเทใจได้นะ', ' เหมียวพร้อมช่วยคุณหาโครงการเสมอนะ', ' ทักมาให้เหมียวเป็นตัวช่วยในการค้นหาโครงงาน'
    # send_message(sender_id, 'เมี๊ยว สวัสดีคุณ'+doc['first_name']+' เหมียวสามารถช่วยคุณค้นหาโครงการในเทใจได้นะ')

    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params={
            'access_token': default_config.FB_PAGE_TOKEN
        },
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
                'recipient': {'id': sender_id},
                'message': messageData
            }
        )
    )
    print(r)
    # "quick_replies":[
    #   {
    #     "content_type":"text",
    #     "title":"<BUTTON_TEXT>",
    #     "image_url":"http://example.com/img/red.png",
    #     "payload":"<STRING_SENT_TO_WEBHOOK>"
    #   }
    # ]

    return

@webhook_blueprint.route('/', methods=['GET'], strict_slashes=False)
def validate_webhook():
    if request.args.get('hub.verify_token', '') == default_config.FB_VERIFY_TOKEN:
        return request.args.get('hub.challenge', '')
    else:
        return 'Wrong validation token'


@webhook_blueprint.route('/', methods=['POST'], strict_slashes=False)
def handle_message():
    data = request.get_json()
    if data and data['object'] == 'page':
        for entry in data['entry']:
            if 'messaging'not in entry:
                for postback_event in entry['standby']:
                    sender_id = postback_event['sender']['id']
                    message_text = postback_event['postback']['title']
                    u = user.find({'sender_id' : sender_id}).sort("_id",-1).limit(1)
                    if u.count() > 0:
                        for doc in u:
                            if message_text.find('ค้นหา') != -1 or message_text.find('ต้องการให้ช่วย') != -1 or message_text.find('ค้นหาใหม่') != -1:
                                searchProject(sender_id, message_text, doc)
                return ''
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    if messaging_event['sender']['id'] == '514129448794599':
                        continue
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']
                    chatState = 0
                    u = user.find({'sender_id' : sender_id}).sort("_id",-1).limit(1)
                    if u.count() > 0:
                        for doc in u:
                            words = tadkaam(message_text)
                            for word in words:
                                if word in greeting_dialog:
                                    greeting(sender_id, message_text, doc)
                                    user.insert({'sender_id' : sender_id,'sender_name':doc['sender_name'] ,'message_text' : message_text, 'chatState' :chatState})
                                    return ''
                            if message_text.find('ค้นหา') != -1 or message_text.find('ต้องการให้ช่วย') != -1 or message_text.find('ค้นหาใหม่') != -1:
                                searchProject(sender_id, message_text,doc)
                            elif doc['chatState'] == 1:
                                searchProject(sender_id,message_text,doc)
                            elif message_text.find('ช่วยเหลือ') != -1 or message_text.find('ทำไรได้บ้าง') != -1:
                                guideline(sender_id, message_text)
                            elif (message_text.find('หมา') != -1 or message_text.find('แมว') != -1) and (message_text.find('ป่วย') != -1 or message_text.find('อาหาร') != -1):
                                send_message(sender_id, 'ขณะนี้เหมียวเทใจยังไม่มีแนวทางรับเรื่องนี้ กรุณาติดต่อช่องทางอื่นๆก่อนนะ แต่ถ้ามีข่าวอัพเดทจะรีบแจ้งให้ทราบนะเมี๊ยว')
                            else:
                                # send_message(sender_id,'ยังไม่เข้าใจอ่ะเมี๊ยว')
                                user.insert({'sender_id' : sender_id,'sender_name':doc['sender_name'] ,'message_text' : message_text, 'chatState' : chatState})
                    else:
                        r = requests.get('https://graph.facebook.com/v2.6/'+sender_id+'?access_token='+default_config.FB_PAGE_TOKEN)
                        data = r.json()
                        user.insert({'sender_id' : sender_id, 'sender_name' : data['first_name'], 'chatState' : 0})
                        k = user.find({'sender_id' : sender_id}).sort("_id",-1).limit(1)
                        for doc in k:
                            greeting(sender_id, message_text,doc)
    return ''

def sendProjectCard(result, sender_id):
    elements = []
    for cardData in result:
        elements.append({"title": cardData['name'], "subtitle" : "เป้าหมาย " + str(cardData['donation_limit']),
                         "image_url":"https://taejai.com/media/" + cardData['cover_image'], "buttons": [{"type":"web_url","url":"https://taejai.com/th/d/"+cardData['slug'],"title":"เวปไซตโครงการ"},{"type":"web_url","title":"บริจาค","url":"https://taejai.com/th/d/" + cardData['slug'] + '/#donate'}]})
    messageData = {
        'attachment':{
            'type': 'template',
            'payload': {
                'template_type':'generic',
                'elements': elements
            }
        }
    }
    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params={
            'access_token': default_config.FB_PAGE_TOKEN
        },
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
                'recipient': {'id': sender_id},
                'message': messageData
            }
        )
    )
    return

def resendPostBack(sender_id, message_text):
    messageData = {
        'attachment':{
            'type': 'template',
            'payload': {
                'template_type':'button',
                'text':message_text,
                    'buttons':[{
                        'type':'postback',
                        'title':'ค้นหาใหม่',
                        'payload':'ค้นหา'
                    }]
                }
            }
        }
    r = requests.post(
        'https://graph.facebook.com/v2.6/me/messages',
        params={
            'access_token': default_config.FB_PAGE_TOKEN
        },
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps({
                'recipient': {'id': sender_id},
                'message': messageData
            }
        )
    )
    return ''

def searchProject(sender_id, message_text,doc):
    if(doc['chatState'] == 0):
        chatState = 1
        send_message(sender_id, 'ให้เหมียวช่วยหาโครงการเกี่ยวกับอะไรดีล่ะ ? ')
        user.insert({'sender_id' : sender_id,'sender_name':doc['sender_name'] ,'message_text' : message_text, 'chatState' : chatState})
    else:
        a = str(datetime.now())
        date = a[0:10]
        taejai = mongo.db.taejai
        predict = predictProject(message_text)
        send_message(sender_id, predict)
        result = taejai.find({'id' : int(predict), 'end_date' : {'$gte' : date}})
        # result = taejai.find({'name' : {'$regex': message_text, '$options' : 'i'}, 'end_date' : {'$gte': date} }).limit(3)
        if result.count() <= 0:
            resendPostBack(sender_id, 'เหมียว ลองหาแล้วแต่ไม่เจอเลยอ่ะ ลองค้นหาใหม่ดูนะ')
            user.insert({'sender_id' : sender_id,'sender_name':doc['sender_name'] ,'message_text' : message_text, 'chatState' : 0})
            return
        sendProjectCard(result, sender_id)
        chatState = 0
        user.insert({'sender_id' : sender_id,'sender_name':doc['sender_name'] ,'message_text' : message_text, 'chatState' : chatState})
    return

def tadkaam(txt):
    bd = PyICU.BreakIterator.createWordInstance(PyICU.Locale("th"))
    bd.setText(txt)
    lastPos = bd.first()
    retTxt = ""
    try:
        while(1):
            currentPos = next(bd)
            retTxt += txt[lastPos:currentPos]
            if(currentPos < len(txt)):
                retTxt += "|"
            lastPos = currentPos
    except StopIteration:
        pass
    words = retTxt.split('|')
    return words

def predictProject(txt):
    k = ''
    result = function.get_result(txt)
    for res in result:
        k += str(res)
    return k


