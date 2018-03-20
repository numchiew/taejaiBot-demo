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
                                    "type" : "web_url",
                                    "title" : "สถานะใบเสร็จ",
                                    "url" : "https://taejai.com/th/request-receipt/"
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

def searchProjectName(text):
    result = article.search(text,client)
    card = []
    for hit in result:
        card.append({"title" : hit.title, "image_url" : "https://taejai.com/media/" + hit['cover_image'] ,"buttons" : [{"type" : "web_url","url" : "https://taejai.com/th/d/" + hit['slug'] + "#donate", "title" : "บริจาค"}, {"type" : "postback", "title" : "ค้นหาใหม่", "payload" : "ค้นหา"}]})
    print(card)
    return card

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
