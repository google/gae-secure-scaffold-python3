import json
import os
import secrets
from typing import Optional

import flask
import flask_talisman
from google.cloud import ndb


class AppConfig(ndb.Model):
    SINGLETON_ID = 'config'

    secret_key = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def singleton(cls):
        config = cls.initial_config()
        obj = cls.get_or_insert(cls.SINGLETON_ID, **config)

        return obj

    @classmethod
    def initial_config(cls):
        config = {
            'secret_key': secrets.token_urlsafe(16),
        }

        return config


def create_app(*args, **kwargs) -> flask.Flask:
    """
    Generate a Flask application with our preferred defaults.

    :param overrides: additional configuration keys / values.
    :return: A Flask Application with our preferred defaults.
    :rtype: Flask
    """
    app = flask.Flask(*args, **kwargs)
    configure_app(app)
    # Defaults to flask_talisman.GOOGLE_SECURITY_POLICY
    csp = app.config['CONTENT_SECURITY_POLICY']
    flask_talisman.Talisman(app, content_security_policy=csp)

    return app


def configure_app(app: flask.Flask):
    """
    Setup the configuration for the Flask app.

    This method is meant to be overridden in the case
    that a Flask app needs extra configuration.

    By default it sets the app Secret Key.

    :param Flask app: The Flask app that requires configuring.
    :param overrides: additional configuration keys / values.
    :return: None
    """
    app.config.from_object('secure_scaffold.settings')
    app.config.from_envvar("FLASK_SETTINGS_FILENAME", silent=True)

    if not app.config['SECRET_KEY']:
        config = get_config_from_datastore()
        app.config['SECRET_KEY'] = config.secret_key


def get_config_from_datastore() -> AppConfig:
    # This happens at application startup, so we use a new NDB context.
    client = ndb.Client()

    with client.context():
        obj = AppConfig.singleton()

    return obj
