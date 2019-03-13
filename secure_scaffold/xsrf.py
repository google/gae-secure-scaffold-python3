from typing import List
from functools import wraps
import hashlib
import hmac

import flask
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadData

from secure_scaffold import settings
from secure_scaffold.contrib.appengine.users import get_current_user


def xsrf_protected(non_xsrf_protected_methods: List[str] = settings.NON_XSRF_PROTECTED_METHODS):
    """
    Decorator to validate XSRF tokens for any methods but GET, HEAD, OPTIONS.

    :param non_xsrf_protected_methods: List of methods (lowercase)
                                        defaults to list from settings (get, head, options)
    """
    def decorated(f):
        @wraps(f)
        def decorator(*args, **kwargs):

            if flask.request.method.lower() in non_xsrf_protected_methods:
                # set cookie
                @flask.after_this_request
                def add_cookie(response):
                    set_token = generate_xsrf_token()
                    response.set_cookie('XSRF-TOKEN', set_token)
                    return response

                return f(*args, **kwargs)
            else:
                # check cookie
                get_token = flask.request.cookies.get('XSRF-TOKEN')
                valid = validate_xsrf_token(get_token)
                if valid:
                    return f(*args, **kwargs)
                else:
                    flask.abort(401)

        return decorator
    return decorated


def generate_xsrf_token():
    """
    Generate a token using the secret key and the user
    We use the URLSafeTimeSerializer to check whether the token times out
    Add the token to the session context
    """
    s = URLSafeTimedSerializer(flask.current_app.secret_key)
    token = hmac.new(flask.current_app.secret_key, get_current_user(), hashlib.sha1()).hexdigest()
    s.dumps(token)

    flask.session['xsrf_token'] = token
    return token


def validate_xsrf_token(token):
    """
    Validate a token against the current session token

    :param token: Token to validate
    :return True/False
    """
    s = URLSafeTimedSerializer(flask.current_app.secret_key)
    try:
        token = s.loads(token, max_age=settings.XSRF_TIME_LIMIT)
    except SignatureExpired:
        # raise Exception("XSRF token has expired")
        return False
    except BadData:
        # raise Exception("XSRF token is invalid")
        return False

    if not hmac.compare_digest(flask.session['xsrf_token'], token):
        # raise Exception("XSRF token does not match")
        return False

    return True
