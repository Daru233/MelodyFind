playlist_id = 'oij2f13823f908sdfuqsdcu'
track_id = '392d145eec574b58'
url = f'/mf/v1/add_to_playlists/{playlist_id}/<string:track_id>'
mock_url = 'https://api.spotify.com/v1/playlists/oij2f13823f908sdfuqsdcu/tracks?uris=%3Cstring:track_id%3E'


def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    response = client.get(url)

    assert response.status_code == 401


def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns401_thenReturn401(client, auth, requests_mock):
    requests_mock.post(mock_url, status_code=401, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns500_thenReturn500(client, auth, requests_mock):
    requests_mock.post(mock_url, status_code=500, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 500


def test_givenValidRequest_whenSpotifyReturns503_thenReturn503(client, auth, requests_mock):
    requests_mock.post(mock_url, status_code=503, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 503


def test_givenValidRequest_whenSpotifyReturns201_thenReturn201(client, auth, requests_mock):
    requests_mock.post(mock_url, status_code=201, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 201

