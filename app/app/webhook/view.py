from flask import Blueprint, request
import requests
import json
from pymongo import MongoClient
from ..config import develop as default_config


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
                    if message_text.find('สวัสดี') != -1:
                        greeting(sender_id, message_text)
                    elif message_text.find('ค้นหา') != -1:
                        searchProject(sender_id, message_text)
                        chatState = 1
                    else:
                        send_message(sender_id, 'ยังไม่เข้าใจอ่ะว่าหมายความว่าอะไร ตอนนี้เราทำได้แค่ค้นหาโครงการนะ')
                    user.insert({'sender_id' : sender_id, 'chatState' : chatState})
    return ''

def searchProject(sender_id, message_text):
    u = user.find_one({'sender_id' : sender_id})
    if u is None:
        print(u)
        if(u['chatState'] == '0'):
            send_message(sender_id, 'ต้องการค้นหาโครงการอะไรครับ')
        else:
            send_message(sender_id, 'ตรงนี้ต้องคิวรี่')
    return




