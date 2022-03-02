from flask import Flask, jsonify, session, request, redirect, make_response
from flask_session import Session
import uuid
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from random import randint, sample
import json
from flask_cors import CORS
import requests
import logging
from logging.config import dictConfig

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('MelodyFind')

app = Flask(__name__)
CLIENT_ID = os.environ.get('Client_ID')
CLIENT_SECRET = os.environ.get('Client_Secret')
REDIRECT_URL = os.environ.get('Heroku_URL')
test_var = os.environ.get('DARU')
print('TEST VARIABLE IS ', test_var)

app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
CORS(app)

categories = ['toplists', 'hiphop', 'workout', 'edm_dance', 'alternative', 'rock', 'gaming', 'punk', 'kpop',
              'pop', 'mood', 'latin', 'indie_alt', 'alternative', 'fresh_finds', 'country', 'classical', 'soul',
              'metal', 'jazz', 'throwback', 'rnb', 'alt']

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder, exist_ok=True)


def session_cache_path():
    return caches_folder + session.get('uuid')


def decorator_is_token_valid(refresh_token_function):
    def wrapper_is_token_valid(arg1, arg2):
        print('Before function')
        refresh_token_function(arg1, arg2)
        print('After function')

    return wrapper_is_token_valid


@decorator_is_token_valid
def print_name(first, last):
    print(first, last)


print_name('Michael', 'Malto')
app.logger.info('This is a log')


@app.route('/callback', methods=['GET'])
def callback():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    old_SCOPES = 'user-read-currently-playing playlist-modify-private'
    SCOPES = 'streaming user-read-email user-read-private user-read-playback-state user-modify-playback-state user-library-read user-library-modify'

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URL,
                                               scope=SCOPES,
                                               cache_handler=cache_handler,
                                               show_dialog=True)

    print(auth_manager.get_cached_token())

    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/callback')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return jsonify("Signed in successfully!", 200)


@app.route('/sign_out')
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror))
    return redirect('/callback')


@app.route('/current_user')
def current_user():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler,
                                               client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URL)

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('/callback')

    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return spotify.current_user()


@app.route("/mf/v1/song", methods=["GET"])
def getARandomSong():
    if not request.args:

        response = []
        categories = ['toplists', 'hiphop', 'workout', 'edm_dance', 'alternative', 'rock', 'gaming', 'punk', 'kpop',
                      'pop']
        playlists = []
        tracks_in_playlist = []

        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                                   client_secret=CLIENT_SECRET))
        random_category_id = categories[randint(0, 9)]

        category_playlists_results = sp.category_playlists(category_id=random_category_id, country='gb')

        for item in category_playlists_results['playlists']['items']:
            playlists.append(item)

        random_playlist = playlists[0]

        FIELDS = 'items.track.album.images, items.track.id, items.track.name, items.track.href, items.track.uri,' \
                 'items.track.artists.href, items.track.artists.id, items.track.artists.name, items.track.artists.uri,' \
                 'items.track.preview_url,' \
                 'total'

        playlist_items_result = sp.playlist_items(
            playlist_id=random_playlist['id'],
            fields=FIELDS,
            additional_types=['track'])

        for item in playlist_items_result['items']:
            tracks_in_playlist.append(item)

        track_to_return = tracks_in_playlist[randint(0, playlist_items_result['total'] - 1)]
        response.append(track_to_return)

        return jsonify(tracks_in_playlist)

    else:

        response = []
        playlists = []
        tracks_in_playlist = []

        category = request.args['category']

        sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                                   client_secret=CLIENT_SECRET))

        category_playlists_results = sp.category_playlists(category_id=category, country='gb')

        for item in category_playlists_results['playlists']['items']:
            playlists.append(item)

        playlist_chosen = playlists[0]

        FIELDS = 'items.track.album.images, items.track.id, items.track.name, items.track.href, items.track.uri,' \
                 'items.track.artists.href, items.track.artists.id, items.track.artists.name, items.track.artists.uri,' \
                 'total'

        playlist_items_result = sp.playlist_items(
            playlist_id=playlist_chosen['id'],
            fields=FIELDS,
            additional_types=['track'])

        for item in playlist_items_result['items']:
            tracks_in_playlist.append(item)

        track_to_return = tracks_in_playlist[randint(0, playlist_items_result['total'] - 1)]
        response.append(playlist_items_result)

        return jsonify(tracks_in_playlist)


@app.route("/", methods=["GET"])
def helloheroku():
    return jsonify({"hello": "world"}, 200)


@app.route("/me/<string:token>", methods=["GET"])
def getProfile(token):
    url = 'https://api.spotify.com/v1/me'

    print(token)

    token = 'BQBLXUJqLcdeWABmMIWgJ57RnuDNtCia3CmqQeKbI0gQVlAS9XHs7-vHBchMXlXyUD5FN2vj4qdBvXNkzx5sxgDldcJe9WO9ZuEQesff9CePMK1vHUpPgi7278ovYIJzHhi-vbWeIBMt_fgGWXhcwjLk8ae4jrfKLIqX9nRXAzB7gGl7jWBT9afR0PI'

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(url, headers=headers)

    return make_response(jsonify({'response': response.json()}, response.status_code))

    # if response.status_code == 401:
    #      # refresh token function
    #     refreshToken(token)
    #     return make_response(jsonify({'response': response.json()}, response.status_code))
    #
    # if response.status_code == 200:
    #     print(response.status_code)
    #     print(response)
    #     return make_response(jsonify({'response': response.json()}, response.status_code))


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


@app.route("/mf/v1/refresh", methods=["GET"])
def refresh():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler,
                                               client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URL)

    return jsonify(auth_manager.get_cached_token())


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
    print("===================== RESPONSE DATA =====================")
    res_data = res.json()
    print(res_data)
    print(res_data['access_token'])
    print(res_data['refresh_token'])

    if res_data.get('error') or res.status_code != 200:
        print("===== response data error =====")
        return make_response(jsonify(res_data, 400))
    else:
        print("===== response success =====")
        response_tokens = {'access_token': res_data['access_token'],
                           'refresh_token': res_data['refresh_token']}
        return make_response(jsonify(response_tokens))


@app.route("/mf/v1/recommendation", methods=["GET"])
def recommendation():
    # no need to check if auth is present because this app api will not be exposed publicly
    # should I still have a check for good practice
    # TODO take in access token as args
    token = request.headers['Authorization'].split()[1]

    # TODO get 5 unique random genre seeds from genre list
    categories_seeds = sample(categories, k=2)

    # TODO use the genre seeds for /recommendations as seeds
    request_url = 'https://api.spotify.com/v1/recommendations'
    params = {'seed_artists': '', 'seed_genres': 'toplists,' + ','.join(categories_seeds), 'seed_tracks': ''}
    print(params)

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json',
    }

    response = requests.get(request_url, params=params, headers=headers)

    # TODO format the returned data so only track, artists and images are returned
    # TODO return the data to react native

    # only checking for 401 because this API will not be exposed publicly
    # will only be accessed through UI interface
    if response.status_code != 200:
        if response.status_code == 401:
            message = 'Spotify API responded with {status_code}, '.format(status_code=str(response.status_code))
            message += response.reason
            app.logger.info(message)
            return make_response(response.json())
        return make_response(response.json())

    tracks = response.json()['tracks']
    for track in tracks:
        del track['available_markets']
        del track['album']['available_markets']


    print(tracks)
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
    res = str(response)
    print(res)

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
