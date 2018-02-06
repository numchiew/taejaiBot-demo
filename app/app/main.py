from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import redis
import requests
import datetime
import PyICU

from .config import develop as default_config

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

@app.route('/tadkaam/<text>')
def isThai(chr):
    cVal = ord(chr)
    if(cVal >= 3584 and cVal <= 3711):
        return True
    return False
def warp(txt):
    #print(txt)
    bd = PyICU.BreakIterator.createWordInstance(PyICU.Locale("th"))
    bd.setText(txt)
    lastPos = bd.first()
    retTxt = ""
    try:
        while(1):
            currentPos = next(bd)
            retTxt += txt[lastPos:currentPos]
            #เฉพาะภาษาไทยเท่านั้น
            if(isThai(txt[currentPos-1])):
                if(currentPos < len(txt)):
                    if(isThai(txt[currentPos])):
                        #คั่นคำที่แบ่ง
                        retTxt += "|"
            lastPos = currentPos
    except StopIteration:
        pass
        #retTxt = retTxt[:-1]
    return jsonify(retTxt)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
