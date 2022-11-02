# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

import flask

import securescaffold.views


demo_app = flask.Flask(__name__)
demo_app.add_url_rule("/", "home", securescaffold.views.lang_redirect)

locale_test_data = [
    # LOCALES, Accept-Language header, expected redirect
    (["en"], "en", "/intl/en/"),
    (["en"], "fr-CH, fr;q=0.9, en;q=0.8, de;q=0.7, *;q=0.5", "/intl/en/"),
    (["en", "fr", "fr-CH"], "fr-CH, fr;q=0.9", "/intl/fr-CH/"),
    (["en", "fr-FR"], "fr-CH", "/intl/fr-FR/"),
    (["en", "fr-FR"], "fr", "/intl/fr-FR/"),
    # Safari on Mac lower-cases language codes.
    (["en", "fr-CH", "fr"], "fr-ch", "/intl/fr-CH/"),
]


class RedirectTestCase(unittest.TestCase):
    def tearDown(self):
        if "LOCALES" in demo_app.config:
            del demo_app.config["LOCALES"]

        if "LOCALES_REDIRECT_TO" in demo_app.config:
            del demo_app.config["LOCALES_REDIRECT_TO"]

    def test_negotiates_valid_locale(self):
        client = demo_app.test_client()
        demo_app.config["LOCALES_REDIRECT_TO"] = "/intl/{locale}/"

        for LOCALES, accept_language, expected in locale_test_data:
            with self.subTest(LOCALES=LOCALES, accept_language=accept_language):
                demo_app.config["LOCALES"] = LOCALES
                headers = [("Accept-Language", accept_language)]

                response = client.get("/", headers=headers)

                self.assertEqual(response.status_code, 302)
                self.assertEqual(response.location, expected)

    def test_default_config_locales(self):
        with self.assertRaises(KeyError):
            demo_app.config["LOCALES"]

        client = demo_app.test_client()
        response = client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/intl/en/")

    def test_default_config_locales_redirect_to(self):
        with self.assertRaises(KeyError):
            demo_app.config["LOCALES_REDIRECT_TO"]

        client = demo_app.test_client()
        response = client.get("/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, "/intl/en/")
