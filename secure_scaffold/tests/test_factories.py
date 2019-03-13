from flask import Flask

from secure_scaffold import factories, settings


def test_app_factory_returns_an_app():
    app = factories.app_factory('testing')

    assert isinstance(app, Flask)
    assert app.name == 'testing'


def test_app_factory_adds_csp_headers():
    app = factories.app_factory()
    client = app.test_client()

    resp = client.get('/')

    expected_headers = '; '.join(
        f'{key} {value}'
        for key, value in settings.CSP_CONFIG.items()
    )

    assert resp.headers['Content-Security-Policy'] == expected_headers
