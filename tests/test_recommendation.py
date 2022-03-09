

# TODO test if request token is missing
def test_givenNoAuth_whenRequestReceived_thenReturn401(client):
    url = '/mf/v1/recommendation'
    response = client.get(url)

    assert response.status_code == 401


# TODO test if request token is not bearer
def test_givenInvalidAuth_whenRequestReceived_thenReturn401(client, invalid_auth):
    url = '/mf/v1/recommendation'
    response = client.get(url, headers=invalid_auth)

    assert response.status_code == 401

