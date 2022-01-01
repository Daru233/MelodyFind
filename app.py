from flask import Flask
import CONSTANTS
import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = CONSTANTS.Client_ID
CLIENT_SECRET = CONSTANTS.Client_Secret


app = Flask(__name__)


@app.route("/")
def hello():

    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
