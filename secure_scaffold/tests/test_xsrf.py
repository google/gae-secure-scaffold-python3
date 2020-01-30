import hmac
import hashlib
from unittest import mock
import os

import pytest
from itsdangerous import URLSafeTimedSerializer

from secure_scaffold import xsrf, settings, factories


app = factories.AppFactory().generate({'SECRET_KEY': 'secret'})


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client


@app.route('/', methods=['GET', 'POST'])
@xsrf.xsrf_protected(non_xsrf_protected_methods=settings.NON_XSRF_PROTECTED_METHODS)
def index():
    return 'Hello World!'


@mock.patch('secure_scaffold.xsrf.os')
def test_xsrf_protected_get_success(mock_os, client):
    random_string = os.urandom(64)
    mock_os.urandom.return_value = random_string
    app.secret_key = b'1234'

    response = client.get('/')

    token = hmac.new(b'1234', random_string, hashlib.sha1).hexdigest()
    s = URLSafeTimedSerializer(b'1234')
    serialized_token = s.dumps(token)

    assert 'XSRF-TOKEN=' + serialized_token in response.headers.get('Set-Cookie')
    assert serialized_token in app.jinja_env.globals['xsrf_token']


@mock.patch('secure_scaffold.xsrf.os')
def test_xsrf_protected_post_success(mock_os, client):
    random_string = os.urandom(64)
    mock_os.urandom.return_value = random_string
    app.secret_key = b'1234'

    client.get('/')

    token = hmac.new(b'1234', random_string, hashlib.sha1).hexdigest()
    s = URLSafeTimedSerializer(b'1234')
    serialized_token = s.dumps(token)

    response = client.post(
        '/',
        data={
            'xsrf': serialized_token
        }
    )

    assert response.status_code == 200
    assert serialized_token in app.jinja_env.globals['xsrf_token']


def test_xsrf_protected_post_fail(client):

    response = client.post(
        '/',
        data={}
    )
    assert response.status_code == 401
    assert response.json['message'] == 'XSRF token required but not given.'


def test_xsrf_protected_post_fail_invalid(client):
    app.secret_key = b'1234'

    client.get('/')

    random_string = os.urandom(64)
    token = hmac.new(b'1234', random_string, hashlib.sha1).hexdigest()
    s = URLSafeTimedSerializer(b'1234')
    serialized_token = s.dumps(token)

    response = client.post(
        '/',
        data={
            'xsrf': serialized_token
        }
    )

    assert response.status_code == 401
    assert serialized_token not in app.jinja_env.globals['xsrf_token']
    assert response.json['message'] == 'XSRF token does not match server token.'
