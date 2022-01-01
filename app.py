from flask import Flask, jsonify
import CONSTANTS
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from random import randint

CLIENT_ID = CONSTANTS.Client_ID
CLIENT_SECRET = CONSTANTS.Client_Secret
REDIRECT_URL = CONSTANTS.Redirect_URL
app = Flask(__name__)


@app.route("/")
def test():
    response = []
    categories = ['toplists', 'hiphop', 'workout', 'edm_dance', 'alternative', 'rock', 'gaming', 'punk', 'kpop', 'pop']
    playlists = []
    tracks_in_playlist = []

    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID,
                                                               client_secret=CLIENT_SECRET))

    random_category_id = categories[randint(0, 9)]

    category_playlists_results = sp.category_playlists(category_id=random_category_id, country='gb')

    for item in category_playlists_results['playlists']['items']:
        playlists.append(item)

    random_playlist = playlists[0]

    playlist_items_result = sp.playlist_items(
        playlist_id=random_playlist['id'],
        fields='items.track.id, items.track.name, items.track.href, items.track.uri, total',
        additional_types=['track'])

    for item in playlist_items_result['items']:
        tracks_in_playlist.append(item)

    track_to_return = tracks_in_playlist[randint(0, playlist_items_result['total']-1)]
    response.append(playlist_items_result)

    return jsonify(track_to_return, 200)


if __name__ == "__main__":
    app.run(debug=True)
