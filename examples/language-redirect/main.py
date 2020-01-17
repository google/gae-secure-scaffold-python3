import flask

import secure_scaffold


DEFAULT_LANGS = ["en"]
DEFAULT_LANGS_REDIRECT_TO = "/intl/{locale}/"


app = flask.Flask(__name__)
app.add_url_rule("/", "lang_redirect", secure_scaffold.views.lang_redirect)
