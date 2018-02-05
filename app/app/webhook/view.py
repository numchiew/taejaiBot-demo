from flask import Blueprint, request
import requests
import json
from pymongo import MongoClient
from ..config import develop as default_config
import datetime

webhook_blueprint = Blueprint('webhook', __name__)
mongo = MongoClient('mongodb://db:27017')

user = mongo.db.users



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
                        'title':'ค้นหา',
                        'payload':'test'
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
                        'title':'ค้นหา',
                        'payload':'test'
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

def greeting(sender_id, message_text):

    messageData = {
        'attachment':{
            'type': 'template',
            'payload': {
                'template_type':'generic',
                'elements':[{
                    'title':'การใช้งานเบิ้องต้น',
                    'subtitle':'สวัสดี ที่ผมทำได้ในขณะนี้คือการค้นหาโครงการ',
                    'image_url':'',
                    'buttons':[{
                        'type':'web_url',
                        'url':'https://taejai.com/th/projects/all/',
                        'title':'เวปไซต์เทใจ'
                    },{
                        'type':'postback',
                        'title':'ค้นหา',
                        'payload':'test'
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
            for messaging_event in entry['messaging']:
                if messaging_event.get('message'):
                    print(messaging_event)
                    if messaging_event['sender']['id'] == '514129448794599':
                        continue
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message']['text']
                    chatState = 0
                    u = user.find({'sender_id' : sender_id}).sort("_id",-1).limit(1)
                    if u.count() > 0:
                        for doc in u:
                            if message_text.find('สวัสดี') != -1 or message_text.find('ทักทาย') != -1:
                                greeting(sender_id, message_text)
                                user.insert({'sender_id' : sender_id, 'chatState' : chatState})
                            elif message_text.find('ค้นหา') != -1:
                                searchProject(sender_id, message_text,doc)
                            elif doc['chatState'] == 1:
                                searchProject(sender_id,message_text,doc)
                            elif message_text.find('ช่วยเหลือ') != -1 or message_text.find('ทำไรได้บ้าง') != -1:
                                guideline(sender_id, message_text)
                            elif (message_text.find('หมา') != -1 or message_text.find('แมว') != -1) and message_text.find('ป่วย') != -1:
                                send_message(sender_id, 'เทใจไม่มีโครงการเกี่ยวกับสัตว์ป่วยนะครับ รบกวนดูช่องทางอื่น')
                            else:
                                send_message(sender_id, 'ยังไม่เข้าใจอ่ะว่าหมายความว่าอะไร ตอนนี้เราทำได้แค่ค้นหาโครงการนะ')
                                user.insert({'sender_id' : sender_id, 'chatState' : chatState})
                    else:
                        send_message(sender_id, 'สวัสดีครับ สำหรับตอนนี้สามารถค้นหาโครงการต่างๆของทางเทใจได้ โดยการพิมพ์ว่า ค้นหา แล้วตามด้วยชื่อโครงการที่สนใจนะครับ')
                        greeting(sender_id, message_text)
                        user.insert({'sender_id' : sender_id, 'chatState' : 0})
    return ''

def sendProjectCard(result, sender_id):
    elements = []
    for cardData in result:
        elements.append({"title": cardData['name'], "subtitle" : "เป้าหมาย " + str(cardData['donation_limit']), "image_url" : "https://taijai.com/media/" + cardData['cover_image'], "buttons": [{"type":"web_url","url":"https://taejai.com/th/projects/all/","title":"เวปไซต์"},{"type":"web_url","title":"บริจาค","url":"https://taejai.com/th/d/" + cardData['slug']}]})
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

def searchProject(sender_id, message_text,doc):
    if(doc['chatState'] == 0):
        chatState = 1
        send_message(sender_id, 'ต้องการค้นหาโครงการอะไรครับ')
        user.insert({'sender_id' : sender_id, 'chatState' : chatState})
    else:
        taejai = mongo.db.taejai
        result = taejai.find({'name' : {'$regex': message_text} }).limit(3)
        if result.count() <= 0:
            send_message(sender_id, 'ขณะนี้ยังไม่มีชื่อโครงการที่ใกล้เคียงกับ ' + message_text + ' นะครับ')
            return
        sendProjectCard(result, sender_id)
        chatState = 0
        user.insert({'sender_id' : sender_id, 'chatState' : chatState})
    return




