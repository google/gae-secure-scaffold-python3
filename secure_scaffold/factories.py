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


class AppFactory:
    """
    Factory to generate a Flask app that includes the security config
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def setup_app_config(self, app: flask.Flask, overrides: Optional[dict] = None):
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

        if overrides:
            app.config.update(overrides)

        if not app.config['SECRET_KEY']:
            config = self.get_config_from_datastore()
            app.config['SECRET_KEY'] = config.secret_key

    @classmethod
    def get_config_from_datastore(cls) -> AppConfig:
        # This happens at application startup, so we use a new NDB context.
        config = cls.default_datastore_config()
        client = ndb.Client()

        with client.context():
            obj = AppConfig.get_or_insert(AppConfig.SINGLETON_ID, **config)

        return obj

    @classmethod
    def default_datastore_config(cls) -> dict:
        config = {
            'secret_key': secrets.token_urlsafe(16),
        }

        return config

    def generate(self, overrides: Optional[dict] = None) -> flask.Flask:
        """
        Generate a Flask application with our preferred defaults.

        :param overrides: additional configuration keys / values.
        :return: A Flask Application with our preferred defaults.
        :rtype: Flask
        """
        app = flask.Flask(*self.args, **self.kwargs)
        self.setup_app_config(app, overrides)
        # Defaults to flask_talisman.GOOGLE_SECURITY_POLICY
        csp = app.config['CONTENT_SECURITY_POLICY']
        flask_talisman.Talisman(app, content_security_policy=csp)

        return app
