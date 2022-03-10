

def test_when_token_missing(client):
    url = '/'
    expected = {'reason': 'token is missing'}
    response = client.get(url)

    assert response.status_code == 401
    assert response.json == expected


def test_when_token_not_bearer(client, auth):
    url = '/'
    expected = {'reason': 'bearer token is required'}
    response = client.get(url, headers=auth['invalid_auth'])

    assert response.status_code == 401
    assert response.json == expected


def test_when_request_valid(client, auth):
    url = '/'
    expected = {'reason': 'hello_world'}
    response = client.get(url, headers=auth['valid_auth'])

    assert response.status_code == 200
    assert response.json == expected


def test_mock_external_api_call(client, auth, requests_mock):
    url = '/'
    requests_mock.get('https://jsonplaceholder.typicode.com/posts/1', status_code=200)

    response = client.get(url, headers=auth['valid_auth'])
    assert response.status_code == 200
