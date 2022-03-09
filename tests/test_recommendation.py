url = '/mf/v1/recommendation'
mock_url = 'https://api.spotify.com/v1/recommendations'


# TODO test if request token is missing
def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    response = client.get(url)

    assert response.status_code == 401


# TODO test if request token is not bearer
def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401


# TODO valid request, spotify returns 401
def test_givenValidRequest_whenSpotifyReturns401_thenReturn401(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=401, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 401


# TODO valid request, spotify returns other
def test_givenValidRequest_whenSpotifyReturns500_thenReturn500(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=500, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 500


# TODO valid request, spotify returns other
def test_givenValidRequest_whenSpotifyReturns503_thenReturn503(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=503, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 503


# TODO valid request, spotify returns 200
def test_givenValidRequest_whenSpotifyReturns200_thenReturn200(client, auth, requests_mock):
    json = {
        'tracks': [
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

    expected_json = [{
        'album': {
            'artist': 'artist_name'
        },
        'track': {'id': ''}
    }]

    requests_mock.get(mock_url, status_code=200, json=json)
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 200
    assert response.json == expected_json
