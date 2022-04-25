import re

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from BackendLogic import StreamLogic, GenerateLogic

GET = "GET"
POST = "POST"

app = Flask(__name__, static_url_path="")
log = app.logger
CORS(app, supports_credentials=True)

app.secret_key = "any random string"
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/generate', methods=['POST'])
def generate():
    content = request.json
    timestamps = content['timestamps']

    if len(timestamps) > 0:
        return jsonify({"address": GenerateLogic.generate_compiation(timestamps)})

    return 'No timestamps provided'

@app.route('/compilation/<id>')
def get_compilation(id):
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]: byte1 = int(groups[0])
        if groups[1]: byte2 = int(groups[1])

    chunk, start, length, file_size = StreamLogic.stream_compilation(id, byte1, byte2)
    resp = Response(
        chunk, 206,
        mimetype='video/webm',
        content_type='video/webm',
        direct_passthrough=True
    )
    resp.headers.add(
        'Content-Range',
        f'bytes {start}-{start + length - 1}/{file_size}'
    )
    return resp



@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response
