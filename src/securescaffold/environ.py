import functools

import flask


X_APPENGINE_QUEUENAME = "X-Appengine-Queuename"
X_APPENGINE_USER_IS_ADMIN = "X-Appengine-User-Is-Admin"


def admin_only(func):
    """Checks the request is from an App Engine administrator."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        request = flask.request

        if is_admin_request(request):
            return func(*args, **kwargs)

        flask.abort(403)

    return _wrapper


def tasks_only(func):
    """Checks the request is from the Tasks scheduler (or an admin).

    This also works for requests from the Tasks scheduler.
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        request = flask.request

        if is_tasks_or_admin_request(request):
            return func(*args, **kwargs)

        flask.abort(403)

    return _wrapper


def is_admin_request(request) -> bool:
    """True if the request was made by a signed-in App Engine administrator."""
    value = request.headers.get(X_APPENGINE_USER_IS_ADMIN)

    return value == "1"


def is_tasks_request(request) -> bool:
    """True if the request is from the Tasks scheduler.

    This also works for requests from the Cron scheduler.
    """
    value = request.headers.get(X_APPENGINE_QUEUENAME)

    return bool(value)


def is_tasks_or_admin_request(request) -> bool:
    """True if the request is from the Tasks scheduler (or an admin)."""
    return is_tasks_request(request) or is_admin_request(request)


is_cron_request = is_tasks_request
cron_only = tasks_only
