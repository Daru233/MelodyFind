url = '/mf/v1/recommendation/' + 'rock'
mock_url = 'https://api.spotify.com/v1/recommendations'
genre = 'rock'
request_url = f'https://api.spotify.com/v1/search?q={genre}&type=track&genre={genre}'


def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    response = client.get(url)

    assert response.status_code == 401


def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns401_thenReturn401(client, auth, requests_mock):
    requests_mock.get(request_url, status_code=401, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns500_thenReturn500(client, auth, requests_mock):
    requests_mock.get(request_url, status_code=500, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 500


def test_givenValidRequest_whenSpotifyReturns503_thenReturn503(client, auth, requests_mock):
    requests_mock.get(request_url, status_code=503, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 503


def test_givenValidRequest_whenSpotifyReturns200_thenReturn200(client, auth, requests_mock):
    example_response_json = {
        'tracks': {
        'items': [
            {
                'available_markets': 'en',
                'album': {
                    'available_markets': [],
                    'artist': 'artist_name'
                },
                'track': {'id': ''}
            }
        ]
    }
    }

    expected_json = {
        'items': [
            {
                'album': {
                    'artist': 'artist_name'
                },
                'track': {'id': ''}
            }
        ]
    }

    requests_mock.get(request_url, status_code=200, json=example_response_json)
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 200
    assert response.json == expected_json
