import unittest

import flask

import secure_scaffold.views


demo_app = flask.Flask(__name__)
demo_app.add_url_rule('/', 'home', secure_scaffold.views.lang_redirect)

locale_test_data = [
    # LOCALES, Accept-Language header, expected redirect
    (['en'], 'en', '/intl/en/'),
    (['en'], 'fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5', '/intl/en/'),
    (['en', 'fr', 'fr-CH'], 'fr-CH, fr;q=0.9', '/intl/fr-CH/'),
    (['en', 'fr-FR'], 'fr-CH', '/intl/fr-FR/'),
    (['en', 'fr-FR'], 'fr', '/intl/fr-FR/'),
]


class RedirectTestCase(unittest.TestCase):
    def tearDown(self):
        if 'LOCALES' in demo_app.config:
            del demo_app.config['LOCALES']

        if 'LOCALES_REDIRECT_TO' in demo_app.config:
            del demo_app.config['LOCALES_REDIRECT_TO']

    def test_negotiates_valid_locale(self):
        client = demo_app.test_client()
        demo_app.config['LOCALES_REDIRECT_TO'] = '/intl/{locale}/'

        for LOCALES, accept_language, expected in locale_test_data:
            with self.subTest(LOCALES=LOCALES, accept_language=accept_language):
                demo_app.config['LOCALES'] = LOCALES
                headers = [('Accept-Language', accept_language)]

                response = client.get('/', headers=headers)

                self.assertEqual(response.status_code, 302)
                _, _, path = response.location.partition('http://localhost')
                self.assertEqual(path, expected)

    def test_default_config_locales(self):
        with self.assertRaises(KeyError):
            demo_app.config['LOCALES']

        client = demo_app.test_client()
        response = client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/intl/en/')

    def test_default_config_locales_redirect_to(self):
        with self.assertRaises(KeyError):
            demo_app.config['LOCALES_REDIRECT_TO']

        client = demo_app.test_client()
        response = client.get('/')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, 'http://localhost/intl/en/')
