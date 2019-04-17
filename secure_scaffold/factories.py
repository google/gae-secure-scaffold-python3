from flask import Flask

from secure_scaffold import settings
from secure_scaffold import xsrf


class AppFactory:
    """
    Factory to generate a Flask app that includes the security config
    """

    def get_name(self) -> str:
        """
        Get the name for the Flask Application.

        This should generally reflect the top level name of
        your application as stated here: http://flask.pocoo.org/docs/1.0/api/

        :return: The name of the application.
        :rtype: str
        """
        return __name__.split('.')[0]

    def setup_app_config(self, app: Flask) -> Flask:
        """
        Setup the configuration for the Flask app.

        This method is meant to be overridden in the case
        that a Flask app needs extra configuration.

        By default it doesn't do anything.

        :param Flask app: The Flask app that requires configuring.
        :return: The configured Flask app.
        :rtype: Flask
        """
        return app

    @staticmethod
    def add_csp_headers(response):
        """
        Generate CSP Headers to be added to a response.

        The CSP headers are generated by inspecting the CSP_CONFIG object
        in the settings module.

        :param response: The response our app has generated which requires headers.
        :return: The response with the required headers.
        """

        csp_headers = '; '.join(
            f'{key} {value}'
            for key, value in settings.CSP_CONFIG.items()
        )
        response.headers['Content-Security-Policy'] = csp_headers

        return response

    def add_app_headers(self, app: Flask) -> Flask:
        """
        Add app specific headers to every response.

        By default we always want CSP headers for an App which by default
        this method will add.

        This method is easily extendable in the case more headers needed to be
        added in any other way.

        :param Flask app: The Flask app that requires the added headers.
        :return: The Flask app with the added headers.
        :rtype: Flask
        """
        app.after_request(self.add_csp_headers)
        return app

    def add_xsrf_error_handler(self, app: Flask) -> Flask:
        """
        Add the xsrf error handler to the app.

        We want xsrf to return verbose error messages and for this we need to
        attach a handler to the app to return the error response correctly.

        :param app: The Flask app to add the handler to.
        :return: The Flask app now with error handler.
        """
        app.register_error_handler(xsrf.XSRFError, xsrf.handle_xsrf_error)
        return app

    def generate(self) -> Flask:
        """
        Generate a Flask application with our preferred defaults.

        :return: A Flask Application with our preferred defaults.
        :rtype: Flask
        """
        app = Flask(self.get_name())
        app = self.setup_app_config(app)
        app = self.add_app_headers(app)
        app = self.add_xsrf_error_handler(app)

        return app
