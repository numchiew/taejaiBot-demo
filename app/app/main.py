from flask import Flask, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import redis
import os

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
    return jsonify({"text": "hello, this is python-flask-fb-chatbot-starter :D"})

@app.route('/create/<username>')
def createUser(username):
	user = mongo.db.users
	if user.find({"name":username}).count():
		return 'already exits:'
	else:
		user.insert({'name' : username})
		return 'successful insert!'


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=80)
