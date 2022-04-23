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
              'pop', 'mood', 'latin', 'indie_alt', 'fresh_finds', 'country', 'classical', 'soul',
              'metal', 'jazz', 'throwback', 'rnb', 'alt']


def auth_required(func):
    @wraps(func)
    def has_token_wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            logger.info('Request does not have authorization')
            return make_response(jsonify({'reason': 'token is missing'}), 401)

        token = token.split()

        if token[0].lower() != 'bearer':
            logger.info('Request does not contain bearer token')
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


@app.route('/mf/v1/playlists', methods=['GET'])
@auth_required
def get_playlists():
    url = 'https://api.spotify.com/v1/me/playlists?limit=20&offset=0'
    token = request.headers['Authorization'].split()[1]
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 401:
            message_401 = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message_401 += response.reason
            except TypeError:
                logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            logger.info(message_401)
            return make_response(jsonify(response.reason), response.status_code)
        message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
        logger.info(message)
        return make_response(jsonify(response.reason), response.status_code)

    playlists = response.json()['items']
    for playlist in playlists:
        del playlist['external_urls']
        del playlist['owner']

    return make_response(jsonify(playlists), 200)


@app.route('/mf/v1/add_to_playlists/<string:playlist_id>/<string:track_id>', methods=['GET'])
@auth_required
def add_to_playlists(playlist_id, track_id):
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={track_id}'
    token = request.headers['Authorization'].split()[1]

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    data = {
        "uris": [track_id],
        'position': 0
    }

    response = requests.post(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 401:
            message_401 = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message_401 += response.reason
            except TypeError:
                app.logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            app.logger.info(message_401)
            return make_response(jsonify(response.reason), response.status_code)
        message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
        app.logger.info(message)
        return make_response(jsonify(response.reason), response.status_code)

    playlists = response.json()['items']
    for playlist in playlists:
        del playlist['external_urls']
        del playlist['owner']

    return make_response(jsonify(playlists), 200)


@app.route("/mf/v1/me", methods=["GET"])
@auth_required
def get_profile():
    REQUEST_URL = "https://api.spotify.com/v1/me"
    token = request.headers['Authorization'].split()[1]

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(REQUEST_URL, headers=headers)
    print(response.reason)

    if response.status_code != 200:
        if response.status_code == 401:
            message_401 = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message_401 += response.reason
            except TypeError:
                logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            logger.info(message_401)
            return make_response(jsonify(response.reason), response.status_code)
        message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
        app.logger.info(message)
        return make_response(jsonify(response.reason), response.status_code)

    response = response.json()

    return make_response(jsonify(response))


@app.route("/exchange/<string:code>", methods=["GET"])
def code_token_exchange(code):
    TOKEN_URL = 'https://accounts.spotify.com/api/token'

    RN_REDIRECT_URL = 'exp://192.168.0.4:19000'

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

    response = requests.post(TOKEN_URL, headers=headers, data=payload)
    res_data = response.json()

    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message += response.reason
            except TypeError:
                logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            logger.info(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    response_tokens = {'access_token': res_data['access_token'],
                       'refresh_token': res_data['refresh_token']}
    return make_response(jsonify(response_tokens), response.status_code)


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
                logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            logger.info(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    tracks = response.json()['tracks']
    for track in tracks:
        del track['available_markets']
        del track['album']['available_markets']

    return make_response(jsonify(tracks), 200)


@app.route("/mf/v1/recommendation/<string:genre>", methods=["GET"])
@auth_required
def genre_recommendation(genre):
    token = request.headers['Authorization'].split()[1]
    request_url = f'https://api.spotify.com/v1/search?q={genre}&type=track&genre={genre}'

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            try:
                message += response.reason
            except TypeError:
                logger.warning('Response reason is not of type str, cannot concat message += response.reason')
            logger.info(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    tracks = response.json()['tracks']
    for track in tracks['items']:
        del track['available_markets']
        del track['album']['available_markets']

    return make_response(jsonify(tracks), 200)


@app.route("/mf/v1/start_playback/<string:track_uri>", methods=["GET"])
@auth_required
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

    if response.status_code != 204:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            message += response.reason
            logger.info(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    return make_response(jsonify({'request': 'success'}), 204)


@app.route("/mf/v1/save_track/<string:track_uri>", methods=["GET"])
@auth_required
def save_track(track_uri):
    print('Inside the save_track method!')
    token = request.headers['Authorization'].split()[1]
    track_uri = track_uri.split(':')[2]
    print(track_uri)
    request_url = f'https://api.spotify.com/v1/me/tracks?ids={track_uri}'

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.put(request_url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            message += response.reason
            logger.warning(message)
            return make_response(jsonify(response.reason), response.status_code)
        return make_response(jsonify(response.reason), response.status_code)

    return make_response(jsonify(response.reason), response.status_code)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, use_reloader=True)
