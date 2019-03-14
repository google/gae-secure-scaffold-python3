import hmac
import hashlib

import pytest
import flask
from itsdangerous import URLSafeTimedSerializer

from secure_scaffold import xsrf, settings
from secure_scaffold.contrib.appengine import users

app = flask.Flask(__name__)


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()

    yield client


@app.route('/', methods=['GET', 'POST'])
@xsrf.xsrf_protected(non_xsrf_protected_methods=settings.NON_XSRF_PROTECTED_METHODS)
def index():
    return 'Hello World!'


def test_xsrf_protected_get_success(client):
    app.secret_key = b'1234'

    response = client.get('/', headers={
            users.USER_EMAIL_HEADER: "test@email.com",
            users.USER_ID_HEADER: "1",
            users.USER_AUTH_DOMAIN_HEADER: "gmail.com",
        })

    user = "test@email.com".encode('utf8')
    token = hmac.new(b'1234', user, hashlib.sha1).hexdigest()
    s = URLSafeTimedSerializer(b'1234')
    serialized_token = s.dumps(token)

    assert 'XSRF-TOKEN=' + serialized_token in response.headers.get('Set-Cookie')


def test_xsrf_protected_post_fail_no_xsrf(client):
    app.secret_key = b'1234'

    response = client.post('/', headers={
            users.USER_EMAIL_HEADER: "test@email.com",
            users.USER_ID_HEADER: "1",
            users.USER_AUTH_DOMAIN_HEADER: "gmail.com",
        })

    assert response.status_code == 401


def test_xsrf_protected_post_fail_invalid_xsrf(client):
    app.secret_key = b'1234'

    client.get('/', headers={
        users.USER_EMAIL_HEADER: "test@email.com",
        users.USER_ID_HEADER: "1",
        users.USER_AUTH_DOMAIN_HEADER: "gmail.com",
    })

    user = "test@email.com".encode('utf8')
    token = hmac.new(b'5678', user, hashlib.sha1).hexdigest()
    s = URLSafeTimedSerializer(b'1234')
    serialized_token = s.dumps(token)

    client.set_cookie('localhost', 'XSRF-TOKEN', serialized_token)
    response = client.post('/', headers={
            users.USER_EMAIL_HEADER: "test@email.com",
            users.USER_ID_HEADER: "1",
            users.USER_AUTH_DOMAIN_HEADER: "gmail.com",
        })

    assert response.status_code == 401


def test_xsrf_protected_post_success(client):
    app.secret_key = b'1234'

    client.get('/', headers={
        users.USER_EMAIL_HEADER: "test@email.com",
        users.USER_ID_HEADER: "1",
        users.USER_AUTH_DOMAIN_HEADER: "gmail.com",
    })

    user = "test@email.com".encode('utf8')
    token = hmac.new(b'1234', user, hashlib.sha1).hexdigest()
    s = URLSafeTimedSerializer(b'1234')
    serialized_token = s.dumps(token)

    client.set_cookie('localhost', 'XSRF-TOKEN', serialized_token)
    response = client.post('/', headers={
            users.USER_EMAIL_HEADER: "test@email.com",
            users.USER_ID_HEADER: "1",
            users.USER_AUTH_DOMAIN_HEADER: "gmail.com",
        })

    assert response.status_code == 200
