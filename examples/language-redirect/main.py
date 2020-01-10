import flask


DEFAULT_LANGS = ["en"]
DEFAULT_LANGS_REDIRECT_TO = "/intl/{locale}/"


def lang_redirect():
    """Redirects the user depending on the Accept-Language header.

    Use this with @flask.before_request or as a view.
    """
    config = flask.current_app.config
    locales = config.get("LOCALES", DEFAULT_LANGS)
    locales_redirect_to = config.get("LOCALES_REDIRECT_TO", DEFAULT_LANGS_REDIRECT_TO)
    locale = flask.request.accept_languages.best_match(locales)
    redirect_to = locales_redirect_to.format(locale=locale)

    return flask.redirect(redirect_to)


app = flask.Flask(__name__)
app.add_url_rule("/", "lang_redirect", lang_redirect)
