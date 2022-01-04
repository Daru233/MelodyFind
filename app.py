from flask import Flask, jsonify, session, request, redirect
from flask_session import Session
import uuid
import os
# import CONSTANTS
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from random import randint
from flask_cors import CORS

# CLIENT_ID = CONSTANTS.Client_ID
# CLIENT_SECRET = CONSTANTS.Client_Secret
# REDIRECT_URL = CONSTANTS.Redirect_URL

app = Flask(__name__)
CLIENT_ID = os.environ.get('Client_ID')
CLIENT_SECRET = os.environ.get('Client_Secret')
REDIRECT_URL = os.environ.get('Heroku_URL')
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)
CORS(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder, exist_ok=True)

def session_cache_path():
    return caches_folder + session.get('uuid')


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
        # return redirect('/callback')

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

        FIELDS = 'items.track.id, items.track.name, items.track.href, items.track.uri,' \
                 'items.track.artists.href, items.track.artists.id, items.track.artists.name, items.track.artists.uri,' \
                 'total'

        playlist_items_result = sp.playlist_items(
            playlist_id=random_playlist['id'],
            fields=FIELDS,
            additional_types=['track'])

        for item in playlist_items_result['items']:
            tracks_in_playlist.append(item)

        track_to_return = tracks_in_playlist[randint(0, playlist_items_result['total'] - 1)]
        response.append(playlist_items_result)

        return jsonify(track_to_return, 200)

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

        FIELDS = 'items.track.id, items.track.name, items.track.href, items.track.uri,' \
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

        return jsonify(track_to_return, 200)


@app.route("/", methods=["GET"])
def helloheroku():
    return jsonify({"hello": "world"}, 200)


# @app.route("/mf/v1/refresh", methods=["GET"])
# def refresh():
#     cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
#     auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler,
#                                                client_id=CLIENT_ID,
#                                                client_secret=CLIENT_SECRET,
#                                                redirect_uri=REDIRECT_URL)
#
#     return jsonify(auth_manager.get_cached_token())


if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
    # app.run(ssl_context='adhoc')
