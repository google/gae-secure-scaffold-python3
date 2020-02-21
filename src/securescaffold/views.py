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

from typing import Optional

import flask
from werkzeug.datastructures import LanguageAccept


DEFAULT_LANGS = ["en"]
DEFAULT_LANGS_REDIRECT_TO = "/intl/{locale}/"


def best_match(requested_langs: LanguageAccept, supported_langs: list) -> Optional[str]:
    result = requested_langs.best_match(supported_langs)

    if result is None:
        # Try again with just the language codes (no country/region codes).
        requested = []

        for code, weight in requested_langs:
            code = code.split("-")[0]
            requested.append((code, weight))

        supported_shorted = [code.split("-")[0] for code in supported_langs]
        result = LanguageAccept(requested).best_match(supported_shorted)

        # If match, convert back to the full language code.
        if result:
            idx = supported_shorted.index(result)
            result = supported_langs[idx]

    return result


def lang_redirect():
    """Redirects the user depending on the Accept-Language header.

    Use this with @flask.before_request or as a view.
    """
    config = flask.current_app.config
    supported_langs = config.get("LOCALES", DEFAULT_LANGS)
    locales_redirect_to = config.get("LOCALES_REDIRECT_TO", DEFAULT_LANGS_REDIRECT_TO)

    locale = best_match(flask.request.accept_languages, supported_langs)

    if locale is None:
        if supported_langs:
            locale = supported_langs[0]
        else:
            locale = DEFAULT_LANGS[0]

    redirect_to = locales_redirect_to.format(locale=locale)

    return flask.redirect(redirect_to)
