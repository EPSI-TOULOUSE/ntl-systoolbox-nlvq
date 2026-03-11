from flask import Flask, abort, jsonify, request

from src.utils.metrics import getCPUStatus, getMemStatus, getOSStatus

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
