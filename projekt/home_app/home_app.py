import hashlib
import os
import re
import uuid

import redis
from flask import Flask, request, jsonify, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.io.VideoFileClip import VideoFileClip

GET = "GET"
POST = "POST"
TOKEN_EXPIRES_IN_SECONDS = 300
SECRET_KEY = "LOGIN_JWT_SECRET"

app = Flask(__name__, static_url_path="")
log = app.logger
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
CORS(app, supports_credentials=True)

app.secret_key = "any random string"
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/generate', methods=['POST'])
def generate():
    content = request.json
    name = str(uuid.uuid4())

    timestamps = content['timestamps']
    video_clips = []
    if len(timestamps) > 0:
        for stamp in timestamps:
            if stamp >= 5:
                stamp = stamp - 5
            video_clips.append(VideoFileClip("Videos/3.mp4").subclip(stamp, stamp + 4))

        final_clip = concatenate_videoclips(video_clips)
        final_clip.write_videofile("Compilations/" + name + ".webm")

        return jsonify({"address": name})

    return 'No timestamps provided'


def get_chunk_compilation(identity, byte1=None, byte2=None):
    full_path = "Compilations/" + identity + ".webm"
    file_size = os.stat(full_path).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.route('/compilation/<identity>')
def get_compilation(identity):
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk_compilation(identity, byte1, byte2)
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


def get_chunk(byte1=None, byte2=None):
    full_path = "Videos/3.mp4"
    file_size = os.stat(full_path).st_size
    start = 0

    if byte1 < file_size:
        start = byte1
    if byte2:
        length = byte2 + 1 - byte1
    else:
        length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)
    return chunk, start, length, file_size


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response
