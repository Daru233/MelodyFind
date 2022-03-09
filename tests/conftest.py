import pytest
import app


@pytest.fixture()
def client():
    client = app.app.test_client()
    yield client


@pytest.fixture()
def auth(valid_auth, invalid_auth):
    auth = {
        'valid_auth': valid_auth,
        'invalid_auth': invalid_auth
    }

    return auth


@pytest.fixture()
def valid_auth():
    headers = {
        'Authorization': 'bearer mockToken123'
    }

    yield headers


@pytest.fixture()
def invalid_auth():
    headers = {
        'Authorization': 'not_bearer mockToken123'
    }

    yield headers

# TODO make a response fixture like auth fixture
