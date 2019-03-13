from unittest import mock

import pytest

from secure_scaffold import constants
from secure_scaffold.contrib.appengine import users


@pytest.fixture
def request():
    with mock.patch("flask.request") as mock_request:
        mock_request.headers = {
            constants.USER_EMAIL_HEADER: "test@email.com",
            constants.USER_ID_HEADER: "1",
            constants.USER_AUTH_DOMAIN_HEADER: "gmail.com",
        }
        yield mock_request


def test_get_header(request):
    request.headers["test-header"] = "test"

    assert users.get_header("test-header") == "test"
    assert not users.get_header("no-header")


def test_is_current_user_admin(request):
    request.headers[constants.USER_ADMIN_HEADER] = "1"
    assert users.is_current_user_admin()

    request.headers[constants.USER_ADMIN_HEADER] = "2"
    assert not users.is_current_user_admin()


def test_gets_user_gets_data_from_headers(request):
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


def test_user_strict(request):
    users.User()

    request.headers[constants.USER_EMAIL_HEADER] = None
    with pytest.raises(users.UserNotFoundError):
        users.User()
    users.User(_strict_mode=False)


def test_user_nickname(request):
    user = users.User()
    assert user.nickname() == "test@email.com"

    request.headers[constants.USER_EMAIL_HEADER] = "test@gmail.com"
    user = users.User()
    assert user.nickname() == "test"


def test_user_hash(request):
    user = users.User()

    assert hash(user) == hash((user.email(), user.auth_domain()))
