from flask import Flask, make_response, request, jsonify, render_template
from flask_cors import CORS
from threading import Thread, Lock
from loguru import logger
from tqdm import tqdm
import requests
import redis
import json
import time
import os


app = Flask(__name__)
CORS(app)

requests.packages.urllib3.disable_warnings()
redis_conn = redis.Redis("127.0.0.1", 6379, 0)


@app.route('/', methods=['GET'])
def api_get_root():
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def api_get_status():
    N = 100
    response = [None] * N
    for i in range(N):
        value = redis_conn.get(f"G{i+1}")
        if value is not None:
            response[i] = int(value.decode())

    return make_response(jsonify(response), 200)


app.run(host='0.0.0.0', port='8888', debug=True)
