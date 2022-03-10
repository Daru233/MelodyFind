from functools import wraps
from flask import Flask, jsonify, request, make_response
import os
from os import path
from random import sample
import json
from flask_cors import CORS
import requests
import logging
from logging.config import dictConfig

LOGGING_CONFIG_FILE = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(LOGGING_CONFIG_FILE)
logger = logging.getLogger('MelodyFind')

app = Flask(__name__)
CLIENT_ID = os.environ.get('Client_ID')
CLIENT_SECRET = os.environ.get('Client_Secret')
REDIRECT_URL = os.environ.get('Heroku_URL')

CORS(app)

categories = ['toplists', 'hiphop', 'workout', 'edm_dance', 'alternative', 'rock', 'gaming', 'punk', 'kpop',
              'pop', 'mood', 'latin', 'indie_alt', 'alternative', 'fresh_finds', 'country', 'classical', 'soul',
              'metal', 'jazz', 'throwback', 'rnb', 'alt']


def auth_required(func):
    @wraps(func)
    def has_token_wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return make_response(jsonify({'reason': 'token is missing'}), 401)

        token = token.split()

        if token[0].lower() != 'bearer':
            return make_response(jsonify({'reason': 'bearer token is required'}), 401)

        return func(*args, **kwargs)

    return has_token_wrapper


@app.route("/", methods=["GET"])
@auth_required
def helloheroku():
    json_placeholder_url = 'https://jsonplaceholder.typicode.com/posts/1'
    response = requests.get(json_placeholder_url)
    status = response.status_code
    return make_response(jsonify({'reason': 'hello_world'}), status)


@app.route('/me/playlists/<string:token>', methods=['GET'])
def get_playlists(token):
    url = 'https://api.spotify.com/v1/me/playlists'
    token = 'BQBBDOHitEMCrKIQvcW7BGadR2KO9MJxwmvSvqPeWvZb26CBGROBDHZK7IY3IUs0c4-OFd-1o9ZnIfenooHHOYLEZKocbPxbytYCE8TareddTpyeyR73ZB_aq-jjQ7edR1PBYa7rDKUdyMti2nfXWbXmKL15kwUxWHCvGvn6CKfiOk63P8jHQXusL1Q'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    data = {
        'offset': 2
    }

    url_with_query = url + '?limit=20&offset=2'

    response = requests.get(url_with_query, headers=headers)
    res = response.reason
    print(res)

    item_count = 0

    # for item in res['items']:
    #     print(item)
    #     item_count += 1
    #
    # print(item_count)

    return make_response(response.json(), response.status_code)
    # return make_response(jsonify({'yeet': 'yeeeet'}))


@app.route("/exchange/<string:code>", methods=["GET"])
def codeTokenExchange(code):
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    RN_REDIRECT_URL = "exp://192.168.0.4:19000"

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': RN_REDIRECT_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    res = requests.post(TOKEN_URL, headers=headers, data=payload)
    res_data = res.json()

    if res_data.get('error') or res.status_code != 200:
        print("===== response data error =====")
        return make_response(jsonify(res_data, 400))
    else:
        print("===== response success =====")
        response_tokens = {'access_token': res_data['access_token'],
                           'refresh_token': res_data['refresh_token']}
        return make_response(jsonify(response_tokens))


@app.route("/mf/v1/recommendation", methods=["GET"])
@auth_required
def recommendation():
    token = request.headers['Authorization'].split()[1]
    categories_seeds = sample(categories, k=1)

    request_url = 'https://api.spotify.com/v1/recommendations'
    params = {'seed_artists': '', 'seed_genres': 'toplists,' + ','.join(categories_seeds), 'seed_tracks': ''}
    print(params)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(request_url, params=params, headers=headers)
    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message += response.reason
            except TypeError:
                app.logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            app.logger.info(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    tracks = response.json()['tracks']
    for track in tracks:
        del track['available_markets']
        del track['album']['available_markets']

    return make_response(jsonify(tracks), 200)


@app.route("/mf/v1/recommendation/<string:genre>", methods=["GET"])
def genre_recommendation(genre):
    token = request.headers['Authorization'].split()[1]
    request_url = 'https://api.spotify.com/v1/recommendations'
    params = {'seed_artists': '', 'seed_genres': genre, 'seed_tracks': ''}

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(request_url, params=params, headers=headers)

    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message += response.reason
            except TypeError:
                app.logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            app.logger.info(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    tracks = response.json()['tracks']
    for track in tracks:
        del track['available_markets']
        del track['album']['available_markets']

    return make_response(jsonify(tracks))


@app.route("/mf/v1/start_playback/<string:track_uri>", methods=["GET"])
def start_playback(track_uri):
    request_url = 'https://api.spotify.com/v1/me/player/play'
    token = request.headers['Authorization'].split()[1]

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    data = {
        "uris": [track_uri]
    }

    response = requests.put(request_url, headers=headers, data=json.dumps(data))

    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            message += response.reason
            app.logger.info(message)
            return make_response(response.reason)
        return make_response(response.reason)

    return make_response(response.status_code)


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
