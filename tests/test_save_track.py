track_uri = 'spotify:track:392d145eec574b58'
url = f'/mf/v1/save_track/{track_uri}'

# mock_url = f'https://api.spotify.com/v1/me/tracks?ids={track_uri}'
mock_url = 'https://api.spotify.com/v1/me/tracks?ids=392d145eec574b58'


def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    response = client.get(url)

    assert response.status_code == 401


def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns401_thenReturn401(client, auth, requests_mock):
    requests_mock.put(mock_url, status_code=401, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns500_thenReturn500(client, auth, requests_mock):
    requests_mock.put(mock_url, status_code=500, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 500


def test_givenValidRequest_whenSpotifyReturns503_thenReturn503(client, auth, requests_mock):
    requests_mock.put(mock_url, status_code=503, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 503