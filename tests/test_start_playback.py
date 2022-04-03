url = '/mf/v1/start_playback/' + 'mockTrackUri'
mock_url = 'https://api.spotify.com/v1/me/player/play'


def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    response = client.get(url)

    assert response.status_code == 401


def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns500_thenReturn500(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=500, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 500


def test_givenValidRequest_whenSpotifyReturns503_thenReturn503(client, auth, requests_mock):
    requests_mock.put(mock_url, status_code=503, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 503


def test_givenValidRequest_whenSpotifyReturns204_thenReturn204(client, auth, requests_mock):

    track_uri = 'mockTrackUri'

    data = {
        "uris": [track_uri]
    }

    requests_mock.put(mock_url, status_code=204)
    response = client.get(url, headers=auth['valid_auth'], data=data)

    assert response.status_code == 204


