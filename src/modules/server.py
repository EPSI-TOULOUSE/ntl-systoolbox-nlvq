from flask import Flask, abort, jsonify, request

from utils.cpu import getCPUStatus
from utils.memory import getMemStatus
from utils.os import getOSStatus

# Create http serveur
app = Flask(__name__)


@app.route('/status')
def getStatus():
    i = request.args.get('i', '')

    if not i:
        abort(400, description='missing query param: i')

    match i:
        case 'os':
            return jsonify(getOSStatus())
        case 'mem':
            return jsonify(getMemStatus())
        case 'cpu':
            return jsonify(getCPUStatus())
