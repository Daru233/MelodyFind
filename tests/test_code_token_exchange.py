url = '/exchange/' + 'mockCode123'
mock_url = 'https://accounts.spotify.com/api/token'


# TODO test if request token is missing
def test_givenNoAuth_whenRequestReceived_thenReturn401(client, auth, requests_mock):

    example_error_response_json = {

    }

    requests_mock.post(mock_url, status_code=400, json=example_error_response_json)

    response = client.get(url)
    assert response.status_code == 400
