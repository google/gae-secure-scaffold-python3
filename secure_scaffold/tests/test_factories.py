from flask import Flask

from secure_scaffold import factories, settings


def test_app_factory_returns_an_app():
    app = factories.AppFactory().generate()

    assert isinstance(app, Flask)


def test_app_factory_adds_csp_headers():
    app = factories.AppFactory().generate()
    client = app.test_client()

    resp = client.get('/')

    expected_headers = '; '.join(
        f'{key} {value}'
        for key, value in settings.CSP_CONFIG.items()
    )

    assert resp.headers['Content-Security-Policy'] == expected_headers


def test_extra_flask_args():
    app = factories.AppFactory(static_url_path='/static').generate()
    assert app.static_url_path == '/static'


def test_given_flask_name():
    app = factories.AppFactory(name='tester').generate()
    assert app.name == 'tester'
