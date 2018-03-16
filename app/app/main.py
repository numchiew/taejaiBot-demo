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

@app.route('/searchProject/<txt>',methods=['GET'])
def searchProject(txt):
    result = article.search(txt,client)
    list = []
    for hit in result:
        print(hit.title)
        list.append({"title" : hit.title, "score" : hit.meta.score})
    return jsonify(list)

@app.route('/botAI', methods=['POST'],strict_slashes=False)
def handle_intent():
    # print('HOOK FROM GOOGLE')
    data = request.get_json()
    print(data)
    intent = data['queryResult']['intent']['displayName']
    if intent == 'greeting':
        sender_id = data['originalDetectIntentRequest']['payload']['data']['sender']['id']
        greeting_ans_dialog_first = ['สวัสดีค่ะคุณ  ', 'สวัสดีคุณ ']
        greeting_ans_dialog_end = [' เหมียวสามารถช่วยคุณค้นหาโครงการได้นะ', ' เหมียวพร้อมช่วยคุณค้นหาโครงการแล้ว', ' ทักมาให้เหมียวเป็นตัวช่วยในการค้นหาโครงการ']
        r = requests.get('https://graph.facebook.com/v2.6/'+sender_id+'?access_token='+default_config.FB_PAGE_TOKEN)
        data = r.json()
        ranNum = random.randrange(len(greeting_ans_dialog_first))
        text = greeting_ans_dialog_first[ranNum]+data['first_name']
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
                                    "title" : "ค้นหาโครงการ",
                                    "payload" : "ค้นหา"
                                },{
                                    "type" : "web_url",
                                    "title" : "สถานะใบเสร็จ",
                                    "url" : "https://taejai.com/th/request-receipt/"
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
                                    "text" : "เหมียว.. ลองค้นหาแล้วไม่เจอเลยอ่ะ ลองค้นหาใหม่ดูนะ",
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
        card.append({"title" : hit.title, "subtitle" : "หมดเขต "+hit.end_date + "\nเป้าหมาย " + str(hit.donation_limit), "image_url" : "https://taejai.com/media/" + hit['cover_image'] ,"buttons" : [{"type" : "web_url","url" : "https://taejai.com/th/d/" + hit['slug'] + "#donate", "title" : "บริจาค"}, {"type" : "postback", "title" : "ค้นหาใหม่", "payload" : "ค้นหา"}]})
    print(card)
    return card

@app.route('/search/<sender_id>')
def search(sender_id):
    r = requests.get('https://graph.facebook.com/v2.6/'+sender_id+'?access_token='+default_config.FB_PAGE_TOKEN)
    data = r.json()
    print(r.json())
    return data['first_name']

@app.route('/predict/<txt>')
def predict(txt):
    a = ''
    b = []
    result = function.get_result(txt)
    for res in result:
        print(res)
        a += str(res)
    return a
    # for res in result:
    #     # a += res
    #     print(res, "====This is RES====")
    #     k = list(res)
    #     return jsonify({"list" : k})
    # print(b)

@app.route('/findName')
def findProjectName():
    res = []
    queryj = ""
    taejai = mongo.db.taejai
    a = str(datetime.now())
    date = a[0:10]
    searchResult = taejai.find({'end_date' : {'$gte' : date}})
    for doc in searchResult:
        res.append({"name":doc["name"]})
        queryj += "{\"name\":"+ (doc["name"]) +"]},"

    print(res)
    data = json.dumps({"taejai":queryj})
    return data

@app.route('/getProject')
def getProject():
    data = []
    a = str(datetime.now())
    date = a[0:10]
    taejai = mongo.db.taejai
    result = taejai.find({})
    for res in result:
        data.append({"id" : res["id"],"name" : res["name"]})
    print(data)
    return jsonify({"data" : data})

@app.route('/findId')
def findId():
    res = []
    queryj = ""
    taejai = mongo.db.taejai
    searchResult = taejai.find({})
    for doc in searchResult:
        res.append({"name":doc["id"]})
        queryj += "{\"name\":"+ str(doc["id"]) +"]},"

    print(res)
    data = json.dumps({"taejai":queryj})
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
