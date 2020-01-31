import json
from unittest import mock

import pytest
from flask import Flask
from google.cloud import ndb

from secure_scaffold import factories, settings
from secure_scaffold import emulator


@pytest.fixture(scope="session")
def datastore():
    """Start and stop the datastore emulator."""
    with emulator.DatastoreEmulatorForTests():
        yield


@pytest.fixture(scope="function")
def ndb_client(datastore):
    client = ndb.Client()

    yield client

    # Now delete all entities.
    with client.context():
        for key in ndb.Query().iter(keys_only=True):
            key.delete_async()


def test_app_factory_returns_an_app(ndb_client):
    app = factories.AppFactory("test").generate()

    assert isinstance(app, Flask)


def test_app_factory_does_not_add_report_to_headers(ndb_client):
    app = factories.AppFactory("test").generate()
    client = app.test_client()

    resp = client.get('/')

    assert "Report-To" not in resp.headers


def test_app_factory_adds_csp_headers(ndb_client):
    app = factories.AppFactory("test").generate()
    client = app.test_client()

    resp = client.get('/')

    expected = (
        "font-src 'self' themes.googleusercontent.com *.gstatic.com; frame-src"
        " 'self' www.google.com www.youtube.com; script-src 'self'"
        " ajax.googleapis.com *.googleanalytics.com *.google-analytics.com;"
        " style-src 'self' ajax.googleapis.com fonts.googleapis.com"
        " *.gstatic.com; default-src 'self' *.gstatic.com")
    assert resp.headers['Content-Security-Policy'] == expected


def test_extra_flask_args(ndb_client):
    app = factories.AppFactory("test", static_url_path='/foo').generate()
    assert app.static_url_path == '/foo'


def test_given_flask_name(ndb_client):
    app = factories.AppFactory("test").generate()
    assert app.name == "test"


def test_new_app_creates_secret_key(ndb_client):
    with mock.patch('secrets.token_urlsafe', return_value='topsecret'):
        app = factories.AppFactory("test").generate()

    with ndb_client.context():
        obj = factories.AppConfig.get_by_id(factories.AppConfig.SINGLETON_ID)
        assert obj.secret_key == app.config['SECRET_KEY']
        assert app.config['SECRET_KEY'] == 'topsecret'


def test_new_app_uses_existing_secret_key(ndb_client):
    with ndb_client.context():
        id_ = factories.AppConfig.SINGLETON_ID
        factories.AppConfig(id=id_, secret_key='hunter2').put()

    app = factories.AppFactory("test").generate()

    assert app.config['SECRET_KEY'] == 'hunter2'
