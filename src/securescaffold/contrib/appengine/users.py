"""
This only works when IAP is enabled for your App Engine instance
"""
import flask


USER_ADMIN_HEADER = "X-Appengine-User-Is-Admin"
USER_AUTH_DOMAIN_HEADER = "X-Appengine-Auth-Domain"
USER_EMAIL_HEADER = "X-Appengine-User-Email"
USER_ID_HEADER = "X-Appengine-User-Id"


class Error(Exception):
    """Base User error type."""


class UserNotFoundError(Error):
    """No email argument was specified, and no user is logged in."""


def requires_auth(func):
    """A decorator that requires a currently logged in user."""
    def decorator(*args, **kwargs):
        try:
            get_current_user()
        except UserNotFoundError:
            flask.abort(401)
        return func(*args, **kwargs)
    return decorator


def requires_admin(func):
    """A decorator that requires a currently logged in administrator."""
    def decorator(*args, **kwargs):
        if not is_current_user_admin():
            flask.abort(401)
        return func(*args, **kwargs)
    return decorator


def get_header(header):
    return flask.request.headers.get(header)


class User:
    def __init__(self, email=None, _auth_domain=None, _user_id=None, _strict_mode=True):
        if not _auth_domain:
            _auth_domain = get_header(USER_AUTH_DOMAIN_HEADER)

        assert _auth_domain

        self._auth_domain = _auth_domain

        if not email:
            email = get_header(USER_EMAIL_HEADER)
        self._email = email

        if not _user_id:
            _user_id = get_header(USER_ID_HEADER)
        self._user_id = _user_id

        if not email and _strict_mode:
            raise UserNotFoundError()

    def nickname(self):
        if (
                self._email
                and self._auth_domain
                and self._email.endswith("@" + self._auth_domain)
        ):
            suffix_len = len(self._auth_domain) + 1
            return self._email[:-suffix_len]
        return self._email

    def email(self):
        return self._email

    def user_id(self):
        return self._user_id

    def auth_domain(self):
        return self._auth_domain

    def __str__(self):
        return str(self.nickname())

    def __repr__(self):
        values = []
        if self._email:
            values.append(f"email='{self._email}'")
        if self._user_id:
            values.append(f"_user_id='{self._user_id}'")
        return f'users.User({",".join(values)})'

    def __hash__(self):
        return hash((self._email, self._auth_domain))


def get_current_user():
    return User()


def is_current_user_admin():
    return get_header(USER_ADMIN_HEADER) == "1"


IsCurrentAdmin = is_current_user_admin
