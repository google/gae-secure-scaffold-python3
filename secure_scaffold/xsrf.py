from typing import List, Optional
from functools import wraps
import hashlib
import hmac
import os

import flask
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadData


class XSRFError(Exception):
    """
    Exception class to return JSON errors.
    This is so we can give more information to the user
    on why their request didn't work.
    """
    status_code = 401

    def __init__(self, message: str, status_code: int = None, payload: dict = None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """
        Combine message and payload into one dict to be returned.
        If payload is None, gives an empty dictionary.

        :return: Dict with key "message" with value of message and converted payload
        """
        response = dict(self.payload or ())
        response['message'] = self.message
        return response


def handle_xsrf_error(error):
    """
    Return a JSON response to the user containing the error
    :param error: XSRFError instance
    :return: Flask JSON response
    """
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def xsrf_protected(non_xsrf_protected_methods: Optional[List[str]] = None):
    """
    Decorator to validate XSRF tokens for any methods but GET, HEAD, OPTIONS.

    :param non_xsrf_protected_methods: List of methods (lowercase)
                                        defaults to list from settings (get, head, options)
    """
    if non_xsrf_protected_methods is None:
        config = flask.current_app.config
        non_xsrf_protected_methods = config['NON_XSRF_PROTECTED_METHODS']

    def decorated(func):
        @wraps(func)
        def decorator(*args, **kwargs):

            if flask.request.method.lower() in non_xsrf_protected_methods:
                # Generate XSRF token
                token = generate_xsrf_token()
                flask.current_app.jinja_env.globals['xsrf_token'] = token

                @flask.after_this_request
                def add_cookie(response):
                    response.set_cookie('XSRF-TOKEN', token)
                    return response

                return func(*args, **kwargs)
            else:
                # Validate XSRF token
                token = flask.request.form.get('xsrf')
                if not token:
                    raise XSRFError("XSRF token required but not given.")

                validate_xsrf_token(token)
                return func(*args, **kwargs)

        return decorator
    return decorated


def generate_xsrf_token():
    """
    Generate a token using the secret key and a random string
    We use the URLSafeTimeSerializer to check whether the token times out
    Add the token to the session context
    Return the serialized token to the user
    """
    serializer = URLSafeTimedSerializer(flask.current_app.secret_key)
    random_string = os.urandom(64)
    token = hmac.new(flask.current_app.secret_key, random_string, hashlib.sha1).hexdigest()
    serialized_token = serializer.dumps(token)

    flask.session['xsrf_token'] = token
    flask.session['session_code'] = random_string
    return serialized_token


def validate_xsrf_token(token):
    """
    Validate a token against the current session token

    :param token: Token to validate (should be serialized)
    :return True/False
    """
    serializer = URLSafeTimedSerializer(flask.current_app.secret_key)
    config = flask.current_app.config

    try:
        token = serializer.loads(token, max_age=config['XSRF_TIME_LIMIT'])
    except SignatureExpired:
        raise XSRFError("XSRF token has expired.")
    except BadData:
        raise XSRFError("XSRF token is invalid.")

    if not hmac.compare_digest(flask.session['xsrf_token'], token):
        raise XSRFError("XSRF token does not match server token.")

    return True
