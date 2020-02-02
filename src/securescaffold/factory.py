import json
import os
import secrets
from typing import Optional

import flask
import flask_talisman
from google.cloud import ndb


class AppConfig(ndb.Model):
    """Datastore model for storing app-wide configuration.

    This is used by `create_app` to save a random value for SECRET_KEY that
    persists across application startup, rather than defining SECRET_KEY in
    your source code.
    """
    SINGLETON_ID = 'config'

    secret_key = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

    @classmethod
    def singleton(cls):
        """Create a datastore entity to store app-wide configuration."""
        config = cls.initial_config()
        obj = cls.get_or_insert(cls.SINGLETON_ID, **config)

        return obj

    @classmethod
    def initial_config(cls):
        """Initial values for app configuration."""
        config = {
            'secret_key': secrets.token_urlsafe(16),
        }

        return config


def create_app(*args, **kwargs) -> flask.Flask:
    """Create a Flask app with secure default behaviours.

    :return: A Flask application.
    :rtype: Flask
    """
    app = flask.Flask(*args, **kwargs)
    configure_app(app)
    # Defaults to flask_talisman.GOOGLE_SECURITY_POLICY
    csp = app.config['CSP_POLICY']
    flask_talisman.Talisman(app, content_security_policy=csp)

    return app


def configure_app(app: flask.Flask):
    """Read configuration and create a SECRET_KEY.

    The configuration is read from "securescaffold.settings", and from the
    filename in the "FLASK_SETTINGS_FILENAME" environment variable (if
    it exists).

    If there is no SECRET_KEY setting, then a random string is generated,
    saved in the datastore, and set.

    :param Flask app: The Flask app that requires configuring.
    :return: None
    """
    app.config.from_object('securescaffold.settings')
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
