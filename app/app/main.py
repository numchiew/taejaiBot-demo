from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import redis
import requests
import datetime
import PyICU
import json

from .config import develop as default_config
from .brain import function

app = Flask(__name__)
app.secret_key = "my-secret"
CORS(app)

mongo = MongoClient('mongodb://db:27017')


redis_client = redis.Redis(
    host=default_config.REDIS_HOST,
    port=default_config.REDIS_PORT)

from .webhook.view import webhook_blueprint as webhook_view
app.register_blueprint(webhook_view, url_prefix='/webhook')


@app.route('/', methods=['GET'])
def index():
    return jsonify({"text": "hello, this is python-flask-fb-chatbot-starter :D ver"})

@app.route('/search/<sender_id>')
def search(sender_id):
	r = requests.get('https://graph.facebook.com/v2.6/'+sender_id+'?access_token='+default_config.FB_PAGE_TOKEN)
	data = r.json()
	print(r.json())
	return data['first_name']

@app.route('/tadkaam/<txt>')

def warp(txt):
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
    return retTxt
@app.route('/predict/<txt>')
def predict(txt):
    a = ''
    result = function.get_result(txt)
    print(result, " =========")
    # for res in result:
    #     a += res
    return jsonify(result)

@app.route('/findName')
def findProjectName():
    res = []
    queryj = ""
    taejai = mongo.db.taejai
    searchResult = taejai.find({})
    for doc in searchResult:
        res.append({"name":doc["name"]})
        queryj += {"name":doc["name"]},

    print(res)
    data = json.dumps({"taejai":queryj})
    return data

@app.route('/findId')
def findId():
    res = []
    queryj = ""
    taejai = mongo.db.taejai
    searchResult = taejai.find({})
    for doc in searchResult:
        res.append({"name":doc["id"]})
        queryj += {"name":doc["id"]},

    print(res)
    data = json.dumps({"taejai":queryj})
    return data

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
