from typing import List
from functools import wraps
import hashlib
import hmac

import flask
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadData

from secure_scaffold import settings
from secure_scaffold.contrib.appengine.users import get_current_user


class XSRFError(Exception):
    status_code = 401

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


def handle_xsrf_error(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


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
                # Generate XSRF token
                token = generate_xsrf_token()
                flask.current_app.jinja_env.globals['xsrf_token'] = token

                @flask.after_this_request
                def add_cookie(response):
                    response.set_cookie('XSRF-TOKEN', token)
                    return response

                return f(*args, **kwargs)
            else:
                # Validate XSRF token
                token = flask.request.form.get('xsrf')
                if not token:
                    raise XSRFError("XSRF token required but not given.")

                try:
                    validate_xsrf_token(token)
                    return f(*args, **kwargs)
                except XSRFError:
                    raise

        return decorator
    return decorated


def generate_xsrf_token():
    """
    Generate a token using the secret key and the user
    We use the URLSafeTimeSerializer to check whether the token times out
    Add the token to the session context
    Return the serialized token to the user
    """
    s = URLSafeTimedSerializer(flask.current_app.secret_key)
    user = get_current_user().__str__().encode('utf8')
    token = hmac.new(flask.current_app.secret_key, user, hashlib.sha1).hexdigest()
    serialized_token = s.dumps(token)

    flask.session['xsrf_token'] = token
    return serialized_token


def validate_xsrf_token(token):
    """
    Validate a token against the current session token

    :param token: Token to validate (should be serialized)
    :return True/False
    """
    s = URLSafeTimedSerializer(flask.current_app.secret_key)
    try:
        token = s.loads(token, max_age=settings.XSRF_TIME_LIMIT)
    except SignatureExpired:
        raise XSRFError("XSRF token has expired.")
    except BadData:
        raise XSRFError("XSRF token is invalid.")

    if not hmac.compare_digest(flask.session['xsrf_token'], token):
        raise XSRFError("XSRF token does not match server token.")

    return True
