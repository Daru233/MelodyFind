url = 'mf/v1/me'
mock_url = 'https://api.spotify.com/v1/me'


def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    response = client.get(url)

    assert response.status_code == 401


def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns401_thenReturn401(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=401, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 401


def test_givenValidRequest_whenSpotifyReturns500_thenReturn500(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=500, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 500


def test_givenValidRequest_whenSpotifyReturns503_thenReturn503(client, auth, requests_mock):
    requests_mock.get(mock_url, status_code=503, text='resp')
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 503


def test_givenValidRequest_whenSpotifyReturnsProfileData_thenReturnProfileData(client, auth, requests_mock):
    example_expected_response = {
        "display_name": "mockProfile",
        "email": "mockProfile@pytest.com",
        "external_urls": {
            "spotify": "url"
        },
        "followers": {
            "href": 'someValue',
            "total": 12
        },
        "href": "href",
        "id": "mockProfile123",
        "images": [
            {
                "height": 'someValue',
                "url": "image",
                "width": 'someValue'
            }
        ],
        "type": "user",
        "uri": "spotify:user:mockProfile"
    }

    example_actual_response = {
        "display_name": "mockProfile",
        "email": "mockProfile@pytest.com",
        "external_urls": {
            "spotify": "url"
        },
        "followers": {
            "href": 'someValue',
            "total": 12
        },
        "href": "href",
        "id": "mockProfile123",
        "images": [
            {
                "height": 'someValue',
                "url": "image",
                "width": 'someValue'
            }
        ],
        "type": "user",
        "uri": "spotify:user:mockProfile"
    }

    requests_mock.get(mock_url, status_code=200, json=example_expected_response)
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 200
    assert example_actual_response == example_expected_response
