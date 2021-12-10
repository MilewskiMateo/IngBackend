import hashlib
import logging
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
TOKEN_EXPIRES_IN_SECONDS = 3000
SECRET_KEY = "LOGIN_JWT_SECRET"

app = Flask(__name__, static_url_path="")
log = app.logger
db = redis.Redis(host="redis-db", port=6379, decode_responses=True)
CORS(app, supports_credentials=True)

app.secret_key = "any random string"

app.config['JWT_TOKEN_LOCATION'] = ["headers"]
app.config["JWT_SECRET_KEY"] = os.environ.get(SECRET_KEY)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = TOKEN_EXPIRES_IN_SECONDS
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['CORS_HEADERS'] = 'Content-Type'

jwt = JWTManager(app)


def setup():
    log.setLevel(logging.DEBUG)


@app.route('/generate', methods=['POST'])
@jwt_required()
def generate():
    content = request.json
    # current_user = get_jwt_identity()
    name = str(uuid.uuid4())

    timestamps = content['timestamps']
    VideoClips = []
    if len(timestamps) > 0:
        for stamp in timestamps:
            if stamp >= 5:
                stamp = stamp - 5
            VideoClips.append(VideoFileClip("Videos/3.mp4").subclip(stamp, stamp + 4))

        final_clip = concatenate_videoclips(VideoClips)
        final_clip.write_videofile("Compilations/" + name + ".webm")

        return jsonify({"address": name})
    else:
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
    resp = Response(chunk, 206, mimetype='video/webm',
                    content_type='video/webm', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
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


@app.route('/video')
def get_file():
    range_header = request.headers.get('Range', None)
    byte1, byte2 = 0, None
    if range_header:
        match = re.search(r'(\d+)-(\d*)', range_header)
        groups = match.groups()

        if groups[0]:
            byte1 = int(groups[0])
        if groups[1]:
            byte2 = int(groups[1])

    chunk, start, length, file_size = get_chunk(byte1, byte2)
    resp = Response(chunk, 206, mimetype='video/mp4',
                    content_type='video/mp4', direct_passthrough=True)
    resp.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return resp


@app.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response


@app.route("/registration/register", methods=["POST"])
def addUser():
    login = request.json['login']
    login_hash = hashlib.sha512(login.encode("utf-8")).hexdigest()
    if (db.exists(login_hash)):
        return jsonify({"responseMessage": "Użytkownik o takim loginie już istnieje"}), 401
    else:
        myDict = request.json
        myDict['password'] = hashlib.sha512(myDict['password'].encode("utf-8")).hexdigest()
        db.hmset(login_hash, myDict)
        return jsonify({"responseMessage": "Udało się"}), 200


@app.route("/login/log", methods=["POST"])
def loginRequest():
    login = request.json['login']
    password_hash = hashlib.sha512(request.json['password'].encode("utf-8")).hexdigest()
    login_hash = hashlib.sha512(login.encode("utf-8")).hexdigest()
    if (db.exists(login_hash)):
        if (db.hget(login_hash, 'password') == password_hash):

            access_token = create_access_token(identity=login_hash)
            return access_token
        else:
            return jsonify({"responseMessage": "Dane logowania niepoprawne"}), 401

    else:
        return jsonify({"responseMessage": "Dane logowania niepoprawne"}), 401


@app.route("/logout", methods=["GET"])
def logout():
    return 'logout'\

@app.route("/videos", methods=["GET"])
def videos():
    return jsonify(mock)

mock = [
    {
        "title": 'Loki',
        "id": 'asdadwd',
        "ulr": 'http:/www/awdwad',
        "image": 'https://terrigen-cdn-dev.marvel.com/content/prod/1x/online_9.jpg',

    }, {
        "title": 'Capitan Marvel',
        "id": 'asdadwd1',
        "ulr": 'http:/www/awdwad',
        "image": 'https://static.posters.cz/image/750/plakaty/captain-marvel-epic-i71851.jpg',

    }, {
        "title": 'Guardian of the Galaxy',
        "id": 'asdadwd2',
        "ulr": 'http:/www/awdwad',
        "image": 'https://m.media-amazon.com/images/I/71pAQsmvQyL._AC_SL1000_.jpg',
    }, {
        "title": 'Infinty Gauntlet',
        "id": 'asdadwd',
        "ulr": 'http:/www/awdwad',
        "image": 'https://static.posters.cz/image/750/plakaty/marvel-retro-the-infinity-gauntlet-i59015.jpg',

    }, {
        "title": 'Loki',
        "id": 'asdadwd',
        "ulr": 'http:/www/awdwad',
        "image": 'https://terrigen-cdn-dev.marvel.com/content/prod/1x/online_9.jpg',
    },
]
