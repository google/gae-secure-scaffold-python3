# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import secrets
from typing import Optional

import flask
import flask_seasurf
import flask_talisman
from google.cloud import ndb


class AppConfig(ndb.Model):
    """Datastore model for storing app-wide configuration.

    This is used by `create_app` to save a random value for SECRET_KEY that
    persists across application startup, rather than defining SECRET_KEY in
    your source code.
    """

    SINGLETON_ID = "config"

    secret_key = ndb.StringProperty()

    @classmethod
    def singleton(cls) -> "AppConfig":
        """Create a datastore entity to store app-wide configuration."""
        config = cls.initial_config()
        obj = cls.get_or_insert(cls.SINGLETON_ID, **config)

        return obj

    @classmethod
    def initial_config(cls) -> dict:
        """Initial values for app configuration."""
        config = {
            "secret_key": secrets.token_urlsafe(16),
        }

        return config


def create_app(*args, **kwargs) -> flask.Flask:
    """Create a Flask app with secure default behaviours.

    :return: A Flask application.
    :rtype: Flask
    """
    app = flask.Flask(*args, **kwargs)
    configure_app(app)

    # Both these extensions can be used as view decorators. Bit worried that
    # this circular reference will cause memory leaks.
    talisman_kwargs = get_talisman_config(app.config)
    app.talisman = flask_talisman.Talisman(app, **talisman_kwargs)
    app.csrf = flask_seasurf.SeaSurf(app)

    return app


def configure_app(app: flask.Flask) -> None:
    """Read configuration and create a SECRET_KEY.

    The configuration is read from "securescaffold.settings", and from the
    filename in the "FLASK_SETTINGS_FILENAME" environment variable (if
    it exists).

    If there is no SECRET_KEY setting, then a random string is generated,
    saved in the datastore, and set.

    :param Flask app: The Flask app that requires configuring.
    :return: None
    """
    app.config.from_object("securescaffold.settings")
    app.config.from_envvar("FLASK_SETTINGS_FILENAME", silent=True)

    if not app.config["SECRET_KEY"]:
        config = get_config_from_datastore()
        app.config["SECRET_KEY"] = config.secret_key


def get_config_from_datastore() -> AppConfig:
    # This happens at application startup, so we use a new NDB context.
    client = ndb.Client()

    with client.context():
        obj = AppConfig.singleton()

    return obj


def get_talisman_config(config: dict) -> dict:
    """Get a dict of keyword arguments to configure flask-talisman."""
    # Talisman doesn't read settings from the Flask app config.
    names = {
        "CSP_POLICY": "content_security_policy",
        "CSP_POLICY_NONCE_IN": "content_security_policy_nonce_in",
        "CSP_POLICY_REPORT_ONLY": "content_security_policy_report_only",
        "CSP_POLICY_REPORT_URI": "content_security_policy_report_uri",
    }

    result = {kwarg: config[setting] for setting, kwarg in names.items()}

    return result
