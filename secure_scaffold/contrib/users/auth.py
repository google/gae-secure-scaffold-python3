import os
from typing import Callable

from flask import blueprints, render_template, abort, session, request, jsonify, redirect, Response

from google.auth.transport import requests
from google.oauth2 import id_token

from secure_scaffold.config import get_setting


class ValidationError(Exception):
    pass


class AuthHandler:
    """
    Handler class for dealing with Authentication in the Secure Scaffold.

    Provides a multitude of easily overrideable methods to customise for
    each projects requirements.
    """
    _AUTH_TEMPLATE_FOLDER_SETTING = 'AUTH_TEMPLATE_FOLDER'
    _CLIENT_ID_SETTING = 'AUTH_OAUTH_CLIENT_ID'

    login_template = 'login.html'
    login_endpoint = '/login'
    authenticate_endpoint = '/authenticate'

    redirect_url = '/'

    def __init__(self, name='auth', url_prefix='/auth'):
        self.blueprint = blueprints.Blueprint(
            name,
            __name__,
            url_prefix=url_prefix,
            template_folder=self.get_template_folder()
        )

        self.blueprint.route(
            self.get_login_endpoint()
        )(self.generate_login_view())
        self.blueprint.route(
            self.get_authenticate_endpoint(),
            methods=('POST',)
        )(self.generate_authenticate_view())

    def get_template_folder(self) -> str:
        """
        Overrideable method to make customising the template folder
        easier to do.
        """
        return get_setting(self._AUTH_TEMPLATE_FOLDER_SETTING)

    def get_login_template(self) -> str:
        """
        Overrideable method to make customising the login template
        easier to do.
        """
        return self.login_template

    def get_client_id(self) -> str:
        """
        Overrideable method to make customising the client_id
        easier to do.
        """
        return get_setting(self._CLIENT_ID_SETTING)

    def get_login_endpoint(self) -> str:
        """
        Overrideable method to make customising the login endpoint
        easier to do.
        """
        return self.login_endpoint

    def get_authenticate_endpoint(self) -> str:
        """
        Overrideable method to make customising the authenticate endpoint
        easier to do.
        """
        return self.authenticate_endpoint

    def get_redirect_url(self) -> str:
        """
        Overrideable method to make customising the authenticate endpoint
        easier to do.
        """
        return self.redirect_url

    def generate_login_view(self) -> Callable:
        """
        Method to generate the view for logging in.

        Generating this inside a method gives us the advantage of providing
        overrideable methods to define some variables within the generated
        function.

        It also makes it simpler to override itself.
        """
        template = self.get_login_template()
        client_id = self.get_client_id()

        def login():
            return render_template(
                template,
                nonce=get_setting('CSP_NONCE'),
                client_id=client_id
            )
        return login

    def generate_authenticate_view(self) -> Callable:
        """
        Method to generate the view for authenticating a login request.

        Generating this inside a method gives us the advantage of providing
        overrideable methods to define some variables within the generated
        function.

        It also makes it simpler to override itself.

        The authentication function also uses multiple class methods itself
        to validate and decide what to return once done.
        """
        client_id = self.get_client_id()

        def authenticate():
            token = request.json.get('token')
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    client_id
                )

                self.check_authentication(idinfo)

                # ID token is valid
                session['logged_in'] = True
                return self.post_authentication()
            except ValidationError:
                abort(400)
        return authenticate

    def check_authentication(self, idinfo) -> bool:
        """
        Check the provided idinfo from Google so that we can
        validate some data around it.

        Currently checks the issuer to ensure it is from google.

        Can be extended to check for other issuers, or ensure an email is from
        a specified domain or any other possible validations.
        """
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValidationError('Wrong issuer.')

        return True

    def post_authentication(self) -> Response:
        """
        Provides the response after authentication has completed.

        Easily overrideable. Currently provides a route to redirect to
        for the frontend.
        """
        return jsonify({'route': self.get_redirect_url()})

    def requires_login(self, func) -> Callable:
        """
        Decorator to enforce a user being logged in for a view to be
        accessible. If the user is not logged in it redirects the user to
        the login URL.
        """
        def wrapper(*args, **kwargs):
            if session.get('logged_in'):
                return func(*args, **kwargs)

            return redirect(
                os.path.join(self.blueprint.url_prefix, self.get_login_endpoint().lstrip('/'))
            )

        return wrapper


try:
    auth_handler = AuthHandler()
except AttributeError:
    raise AttributeError('Setting "AUTH_OAUTH_CLIENT_ID"" does not exist. '
                         'To use secure_scaffold.contrib.users.auth this '
                         'setting must be defined.')

auth_blueprint = auth_handler.blueprint
