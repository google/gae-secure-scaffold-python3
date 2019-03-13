from flask import Flask

from secure_scaffold import settings


def app_factory(name: str = __name__.split('.')[0]) -> Flask:
    app = Flask(name)

    @app.after_request
    def add_csp_headers(response):
        csp_headers = '; '.join(
            f'{key} {value}'
            for key, value in settings.CSP_CONFIG.items()
        )
        response.headers['Content-Security-Policy'] = csp_headers

        return response

    return app
