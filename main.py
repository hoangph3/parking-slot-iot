from flask import Flask, make_response, jsonify, render_template
from flask_cors import CORS
from threading import Thread
import requests

from jobs.observer import execute
from keeper.connections import DBConnector
from keeper.environments import SystemEnv

requests.packages.urllib3.disable_warnings()
redis_conn = DBConnector.redis_connection
app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def api_get_root():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def api_get_status():
    N = SystemEnv.num_slots
    response = [None] * N
    for i in range(N):
        value = redis_conn.get(i+1)
        if value is not None:
            response[i] = int(value.decode())

    return make_response(jsonify(response), 200)


if __name__ == "__main__":
    # run job
    Thread(target=execute).start()
    # run api
    app.run(host='0.0.0.0', port=SystemEnv.api_port, debug=True)
