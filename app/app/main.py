from flask import Flask, jsonify, request
from flask_cors import CORS
from pymongo import MongoClient
import redis
import requests
import datetime
import json
from datetime import datetime
from elasticsearch import Elasticsearch
from .config import develop as default_config
from .brain import function
from .brain import article
from elasticsearch_dsl.connections import connections
import random

app = Flask(__name__)
app.secret_key = "my-secret"
CORS(app)

mongo = MongoClient('mongodb://db:27017')
client = connections.create_connection(host='128.199.70.132')
print("================",client,"================")

redis_client = redis.Redis(
    host=default_config.REDIS_HOST,
    port=default_config.REDIS_PORT)

from .webhook.view import webhook_blueprint as webhook_view
app.register_blueprint(webhook_view, url_prefix='/webhook')

# @app.route('/searchProject/<txt>')
# def searchProject(txt):
#
#     result = Article.search(txt)
#     for res in result:
#         print(result)
#     return result


@app.route('/', methods=['GET'])
def index():
    return jsonify({"text": "hello, this is python-flask-fb-chatbot-starter :D ver"})

@app.route('/botAI', methods=['POST'],strict_slashes=False)
def handle_intent():
    # print('HOOK FROM GOOGLE')
    k = json.dumps({})
    data = request.get_json()
    print(data)
    intent = data['queryResult']['intent']['displayName']
    if intent == 'greeting':
        sender_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        greeting_ans_dialog_first = ['สวัสดีค่ะคุณ  ', 'สวัสดีคุณ ']
        lt =  '\nระหว่างรอแอดมินมาตอบให้ช่วยเหลืออะไรดีคะ'
        greeting_ans_dialog_end = [' เหมียวสามารถช่วยคุณค้นหาโครงการได้นะ', ' เหมียวพร้อมช่วยคุณค้นหาโครงการแล้ว', ' ทักมาให้เหมียวเป็นตัวช่วยในการค้นหาโครงการ']
        r = requests.get('https://graph.facebook.com/v2.6/'+sender_id+'?access_token='+default_config.FB_PAGE_TOKEN)
        data = r.json()
        print(data)
        ranNum = random.randrange(len(greeting_ans_dialog_first))
        text = greeting_ans_dialog_first[ranNum]+data['first_name'] + lt
        k = json.dumps({
            "fulfillmentMessages" : [{
                "platform" : "FACEBOOK",
                "payload" : {
                    "facebook" : {
                        "attachment" : {
                            "type" : "template",
                            "payload" : {
                                "template_type" : "button",
                                "text" : text,
                                "buttons" : [{
                                    "type" : "postback",
                                    "title" : "แจ้งปัญหา",
                                    "payload" : "แจ้งปัญหา"
                                },{
                                    "type" : "postback",
                                    "title" : "สถานะใบเสร็จ",
                                    "payload" : "สถานะใบเสร็จ"
                                },{
                                    "type" : "web_url",
                                    "title" : "ส่งโครงการ",
                                    "url" : "https://taejai.com/th/submission/"
                                }]
                            }
                        }
                    }
                }
            }]
        })
    elif intent == 'request-receipt':
        donate_id = data['queryResult']['queryText']
        card = searchReceipt(donate_id)
        k = json.dumps({
                "fulfillmentMessages" : [{
                    "platform" : "FACEBOOK",
                    "payload" : {
                        "facebook" : {
                            "attachment" : {
                                "payload" : {
                                    "template_type" : "generic",
                                    "elements" : card
                                },
                                "type" : "template"
                            }
                        }
                    }
                }]
            })
    elif intent == 'request-receipt - hasInvoice - False' or intent == 'request-receipt - hasInvoice - False - no':
        param = data['queryResult']['parameters']
        dialog = "ใบเสร็จจะถูกส่งไปในชื่อ " + param['name'] + " ที่อยู่ " + param['address']+ " ทางอีเมลล์ที่คุณใช้ในการบริจาค"
        k = json.dumps({
            "fulfillmentMessages" : [{
                "platform" : "FACEBOOK",
                "payload" : {
                    "facebook" : {
                        "attachment" : {
                            "type" : "template",
                            "payload" : {
                                "template_type" : "button",
                                "text" : dialog,
                                "buttons" : [{
                                    "type" : "postback",
                                    "title" : "ตกลง",
                                    "payload" : "ใช่"
                                },{
                                    "type" : "postback",
                                    "title" : "แก้ไข",
                                    "payload" : "ไม่"
                                }]
                            }
                        }
                    }
                }
            }]
        })
    elif intent == 'request-receipt - hasInvoice - False - yes':
        k = json.dumps({
            "fulfillmentMessages" : [{
                "platform" : "FACEBOOK",
                "payload" : {
                    "facebook" : {
                        "attachment" : {
                            "type" : "template",
                            "payload" : {
                                "template_type" : "button",
                                "text" : "คุณต้องการให้จัดส่งทางไปรษณีย์หรือไม่",
                                "buttons" : [{
                                    "type" : "postback",
                                    "title" : "ต้องการ",
                                    "payload" : "ส่งไปรษณีย์"
                                },{
                                    "type" : "postback",
                                    "title" : "ไม่ต้องการ",
                                    "payload" : "ไมต้องส่ง่"
                                }]
                            }
                        }
                    }
                }
            }]
        })
    elif intent == 'post - confirm':
        k = json.dumps({
            "fulfillmentMessages" : [{
                "platform" : "FACEBOOK",
                "payload" : {
                    "facebook" : {
                        "attachment" : {
                            "type" : "template",
                            "payload" : {
                                "template_type" : "button",
                                "text" : "ต้องการให้จัดส่งที่อยู่เดียวกับที่กรอกหรือไม่",
                                "buttons" : [{
                                    "type" : "postback",
                                    "title" : "ใช่",
                                    "payload" : "ที่อยู่เดิม"
                                },{
                                    "type" : "postback",
                                    "title" : "แก้ไข",
                                    "payload" : "จะเปลี่ยนที่อยู่"
                                }]
                            }
                        }
                    }
                }
            }]
        })
    elif intent == 'post - confirm - edit - location' or intent == 'post - confirm - edit - location - again':
        param = data['queryResult']['parameters']
        k = json.dumps({
            "fulfillmentMessages" : [{
                "platform" : "FACEBOOK",
                "payload" : {
                    "facebook" : {
                        "attachment" : {
                            "type" : "template",
                            "payload" : {
                                "template_type" : "button",
                                "text" : "ที่อยู่สำหรับการจัดส่งคือ " + param['postAddress'],
                                "buttons" : [{
                                    "type" : "postback",
                                    "title" : "ใช่",
                                    "payload" : "ส่งเลย"
                                },{
                                    "type" : "postback",
                                    "title" : "แก้ไข",
                                    "payload" : "ขอเปลี่ยนอีกครั้ง"
                                }]
                            }
                        }
                    }
                }
            }]
        })
    elif intent == 'request-receipt - hasInvoice - True':
        param = data['queryResult']['parameters']['number']
        # do request here.
    elif intent == 'send with no post':
        contexts = data['queryResult']['outputContexts']
        json_len = len(contexts)
        param = contexts[json_len -1]['parameters']
        sendReceipt(param['order_id.original'], param['name.original'], param['address.original'], "")
    elif intent == 'post - same - location':
        contexts = data['queryResult']['outputContexts']
        json_len = len(contexts)
        param = contexts[json_len -1]['parameters']
        # print("param" , param)
        # print('PARAMETER+++++++++++++++++', param['name.original'], param['order_id.original'], param['detail.original'], param['address.original'])
        sendReceipt(param['order_id.original'], param['name.original'], param['address.original'], param['address.original'])
    elif intent == 'post - confirm - edit - location - confirm':
        donorAddress = data['queryResult']['outputContexts'][0]['parameters']
        contexts = data['queryResult']['outputContexts']
        json_len = len(contexts)
        param = contexts[json_len -1]['parameters']
        sendReceipt(param['order_id.original'], param['name.original'], param['address.original'], donorAddress['postAddress.original'])
    elif intent == 'post - confirm - no':
        param = data['queryResult']['parameters']
        dialog = "ใบเสร็จจะถูกส่งไปที่ " + param['address']
        k = json.dumps({
            "fulfillmentMessages" : [{
                "platform" : "FACEBOOK",
                "payload" : {
                    "facebook" : {
                        "attachment" : {
                            "type" : "template",
                            "payload" : {
                                "template_type" : "button",
                                "text" : dialog,
                                "buttons" : [{
                                    "type" : "postback",
                                    "title" : "ใช่",
                                    "payload" : "ใช่"
                                },{
                                    "type" : "postback",
                                    "title" : "แก้ไข",
                                    "payload" : "ไม่"
                                }]
                            }
                        }
                    }
                }
            }]
        })
    elif intent == 'search':
        print(data)
        text = data['queryResult']['queryText']
        card = searchProjectName(text)
        if len(card) == 0:
            k = json.dumps({
                "fulfillmentMessages" : [{
                    "platform" : "FACEBOOK",
                    "payload":{
                        "facebook" : {
                            "attachment" : {
                                "type" : "template",
                                "payload" : {
                                    "template_type" : "button",
                                    "text" : "ลองค้นหาแล้วไม่เจอเลยอ่ะ ลองค้นหาใหม่ดูนะ",
                                    "buttons" : [{
                                        "type" : "postback",
                                        "title" : "ค้นหาใหม่",
                                        "payload" : "ค้นหา"
                                    }]
                                }
                            }
                        }
                    }
                }]
            })
        else:
            k = json.dumps({
                "fulfillmentMessages" : [{
                    "platform" : "FACEBOOK",
                    "payload" : {
                        "facebook" : {
                            "attachment" : {
                                "payload" : {
                                    "template_type" : "generic",
                                    "elements" : card
                                },
                                "type" : "template"
                            }
                        }
                    }
                }]
            })
    else:
        k = json.dumps({})
    print(k)

    return k

def sendReceipt(nodeId, name ,address , donorAddress):
    payload = {"query":"mutation RequestReceiptMutation(\n  $input: RequestReceiptInput!\n) {\n  requestReceipt(input: $input) {\n    donation {\n      id\n    }\n  }\n}\n","variables":{"input":{"id":nodeId,"invoiceAddressee":name,"invoiceAddress":address,"donorAddress":donorAddress}}}
    r = requests.post(
        'https://taejai.com/graphql',
        headers={
            'Content-Type': 'application/json'
        },
        json = payload
    )
    print(r)
    return r

def searchProjectName(text):
    result = article.search(text,client)
    card = []
    for hit in result:
        card.append({"title" : hit.title, "image_url" : "https://taejai.com/media/" + hit['cover_image'] ,"buttons" : [{"type" : "web_url","url" : "https://taejai.com/th/d/" + hit['slug'] + "#donate", "title" : "บริจาค"}, {"type" : "postback", "title" : "ค้นหาใหม่", "payload" : "ค้นหา"}]})
    print(card)
    return card

def searchReceipt(donate_id):
    payload = {"query":"query DonationListQuery(\n  $text: String!\n) {\n  donations(text: $text) {\n    edges {\n      node {\n        ...Donation_donation\n        id\n      }\n    }\n  }\n}\n\nfragment Donation_donation on Donation {\n  id\n  created\n  hasInvoice\n  isRequestReceipt\n  project {\n    name\n    id\n  }\n}\n","variables":{"text":donate_id}}
    r = requests.post(
        'https://taejai.com/graphql',
        headers={
            'Content-Type': 'application/json'
        },
        json = payload
        )
    data = json.loads(r.text)
    nodes = data['data']['donations']['edges']
    print(nodes,"===============================")
    card = []
    strButton = ''
    for i in nodes:
        if(i['node']['hasInvoice']):
            strButton = 'ขอใบเสร็จอีกครั้ง'
        else:
            strButton = 'ขอใบเสร็จ'
        date = str(i['node']['created'])
        card.append({"title" : "โครงการ "+i['node']['project']['name'], "subtitle" : "บริจาคเมื่อ " + date[0:10], "buttons" : [{"type" : "postback", "title" : strButton, "payload" : strButton+ " " + i['node']['id']}]})
    return card

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
