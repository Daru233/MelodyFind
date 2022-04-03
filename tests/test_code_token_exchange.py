url = '/exchange/' + 'mockCode123'
mock_url = 'https://accounts.spotify.com/api/token'


def test_givenInvalidCode_whenRequestReceived_thenReturn400(client, requests_mock):
    example_error_response_json = {
    }

    requests_mock.post(mock_url, status_code=400, json=example_error_response_json)
    response = client.get(url)

    assert response.status_code == 400


def test_givenValidCode_whenRequestReceived_thenReturn200(client, requests_mock):
    example_response_json = {
        'access_token': 'mockAccessToken',
        'refresh_token': 'mockRefreshToken'
    }

    requests_mock.post(mock_url, status_code=200, json=example_response_json)
    response = client.get(url)

    assert response.status_code == 200


def test_givenValidCode_whenSpotifyRespondsWith503_thenReturn503(client, requests_mock):
    example_error_response_json = {
        'access_token': 'mockAccessToken',
        'refresh_token': 'mockRefreshToken'
    }

    requests_mock.post(mock_url, status_code=503, json=example_error_response_json)
    response = client.get(url)

    assert response.status_code == 503
