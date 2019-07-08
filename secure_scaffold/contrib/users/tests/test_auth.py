from importlib import reload
from unittest import mock

import pytest
from flask import Blueprint, Flask
from werkzeug.test import Client


def test_import_no_setting_fails():
    with pytest.raises(AttributeError):
        from secure_scaffold.contrib.users import auth
        reload(auth)


@pytest.fixture
def _patched_settings(request):
    from secure_scaffold import settings
    settings.AUTH_OAUTH_CLIENT_ID = 'test'

    return settings


@pytest.fixture
def app(_patched_settings) -> Flask:
    from secure_scaffold.factories import AppFactory
    from secure_scaffold.contrib.users.auth import auth_blueprint

    app = AppFactory().generate()

    app.register_blueprint(auth_blueprint)

    return app


@pytest.fixture
def client(app) -> Client:
    return app.test_client()


@pytest.fixture
def _context(app) -> Client:
    with app.test_request_context():
        yield app.test_client()


def test_init_handler(_patched_settings):
    from secure_scaffold import settings
    settings.AUTH_OAUTH_CLIENT_ID = 'test'
    from secure_scaffold.contrib.users import auth

    assert isinstance(auth.auth_handler, auth.AuthHandler)
    assert isinstance(auth.auth_blueprint, Blueprint)


def test_get_template_folder(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    assert auth_handler.get_template_folder() == _patched_settings.AUTH_TEMPLATE_FOLDER


def test_get_template(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    assert auth_handler.get_login_template() == auth_handler.login_template


def test_get_client_id(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    assert auth_handler.get_client_id() == 'test'


def test_get_login_endpoint(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    assert auth_handler.get_login_endpoint() == auth_handler.login_endpoint


def test_get_authenticate_endpoint(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    assert auth_handler.get_authenticate_endpoint() == auth_handler.authenticate_endpoint


def test_get_redirect_url(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    assert auth_handler.get_redirect_url() == auth_handler.redirect_url


def test_check_authentication(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler
    idinfo = {
        'iss': 'accounts.google.com'
    }
    assert auth_handler.check_authentication(idinfo)


def test_check_authentication_invalid(_patched_settings):
    from secure_scaffold.contrib.users.auth import auth_handler, ValidationError

    with pytest.raises(ValidationError):
        idinfo = {
            'iss': 'bad.provider.com'
        }
        auth_handler.check_authentication(idinfo)


def test_post_authentication(_context):
    from secure_scaffold.contrib.users.auth import auth_handler

    response = auth_handler.post_authentication()
    assert response.status_code == 200
    assert response.json == {'route': '/'}


def test_login(client: Client):
    resp = client.get('/auth/login')
    assert resp.status_code == 200
    assert b'<div class="g-signin2" data-onsuccess="onSignIn"></div>' in resp.data


@mock.patch('secure_scaffold.contrib.users.auth.id_token')
def test_authenticate(mock_token, client: Client):
    mock_token.verify_oauth2_token.return_value = {
        'iss': 'accounts.google.com'
    }

    resp = client.post('/auth/authenticate', json={'token': 'test'})

    assert resp.status_code == 200
    assert resp.json == {'route': '/'}


@mock.patch('secure_scaffold.contrib.users.auth.id_token')
def test_authenticate_fail(mock_token, client: Client):
    mock_token.verify_oauth2_token.return_value = {
        'iss': 'bad_provider'
    }

    resp = client.post('/auth/authenticate', json={'token': 'test'})

    assert resp.status_code == 400


def test_requires_login(app):
    from secure_scaffold.contrib.users.auth import auth_handler

    @app.route('/')
    @auth_handler.requires_login
    def test_view():
        return 'OK'

    client = app.test_client()
    resp = client.get('/')

    assert resp.location.endswith('/auth/login')
    assert resp.status_code == 302

    with client.session_transaction() as session:
        session['logged_in'] = True

    resp = client.get('/')

    assert resp.status_code == 200
    assert resp.data == b'OK'
