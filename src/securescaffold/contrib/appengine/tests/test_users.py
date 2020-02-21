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

import contextlib
from unittest import mock

import flask
import pytest
from werkzeug.exceptions import HTTPException

from securescaffold.contrib.appengine import users


@contextlib.contextmanager
def request_context(admin=None, email=None, auth_domain="example.com", id=None):
    """Helper to populate `flask.request` with security headers."""
    app = flask.Flask("test")
    headers = []

    if admin:
        headers.append((users.USER_ADMIN_HEADER, admin))

    if email:
        headers.append((users.USER_EMAIL_HEADER, email))

    if auth_domain:
        headers.append((users.USER_AUTH_DOMAIN_HEADER, auth_domain))

    if id:
        headers.append((users.USER_ID_HEADER, id))

    with app.test_request_context(headers=headers):
        yield


def test_requires_auth_decorator_success():
    func = mock.MagicMock()
    decorated_req = users.requires_auth(func)

    with request_context(email="alice@example.com"):
        decorated_req()

    assert func.call_args_list == [mock.call()]


def test_requires_auth_decorator_fail():
    func = mock.MagicMock()
    decorated_req = users.requires_auth(func)
    with pytest.raises(HTTPException):
        try:
            with request_context():
                decorated_req()
        except HTTPException as e:
            assert e.code == 401
            raise
    assert not func.called


def test_requires_admin_decorator_success():
    func = mock.MagicMock()
    decorated_req = users.requires_admin(func)

    with request_context(admin="1"):
        decorated_req()

    assert func.called


def test_requires_admin_decorator_fail():
    func = mock.MagicMock()
    decorated_req = users.requires_admin(func)
    with pytest.raises(HTTPException):
        try:
            with request_context(admin="2"):
                decorated_req()
        except HTTPException as e:
            assert e.code == 401
            raise
    assert not func.called


def test_get_header():
    app = flask.Flask("test")
    headers = [("test-header", "test")]

    with app.test_request_context(headers=headers):
        assert users.get_header("test-header") == "test"
        assert not users.get_header("no-header")


def test_is_current_user_admin():
    with request_context(email="alice@example.com", admin="1"):
        assert users.is_current_user_admin()

    with request_context(email="alice@example.com", admin="2"):
        assert not users.is_current_user_admin()


def test_gets_user_gets_data_from_headers():
    with request_context(email="test@email.com", auth_domain="gmail.com", id="1"):
        user = users.get_current_user()

    assert user.email() == "test@email.com"
    assert user.user_id() == "1"
    assert user.auth_domain() == "gmail.com"


def test_user_with_kwargs():
    user = users.User(
        email="mytestemail@email.com", _user_id="2", _auth_domain="gmail.com"
    )

    assert user.email() == "mytestemail@email.com"
    assert user.user_id() == "2"
    assert user.auth_domain() == "gmail.com"


def test_user_strict():
    with pytest.raises(users.UserNotFoundError):
        with request_context():
            users.User()

    with request_context():
        users.User(_strict_mode=False)


def test_user_nickname():
    with request_context(email="test@gmail.com", auth_domain="example.com"):
        user = users.User()
        assert user.nickname() == "test@gmail.com"

    with request_context(email="test@gmail.com", auth_domain="gmail.com"):
        user = users.User()
        assert user.nickname() == "test"


def test_user_hash():
    with request_context(email="alice@example.com"):
        user = users.User()

        assert hash(user) == hash((user.email(), user.auth_domain()))
