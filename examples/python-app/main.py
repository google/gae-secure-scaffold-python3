import os
import re
import unicodedata

import flask
import markupsafe
import mistune
import securescaffold


app = securescaffold.create_app(__name__)


@app.route("/")
def about():
    """One-page introduction to Secure Scaffold."""

    with open("README-secure-scaffold.md") as fh:
        m = mistune.Markdown(renderer=Anchors())
        readme = m.render(fh.read())
        readme = markupsafe.Markup(readme)

    context = {
        "page_title": "Secure Scaffold",
        "readme": readme,
    }

    return flask.render_template("about.html", **context)


@app.route("/csrf", methods=["GET", "POST"])
def csrf():
    """Demonstration of using CSRF to protect a form."""
    context = {
        "page_title": "CSRF protection",
        "message": "",
    }

    if flask.request.method == "POST":
        first_name = flask.request.form.get("first-name")

        if first_name:
            context["message"] = f"Hello {first_name}!"

    return flask.render_template("csrf.html", **context)


@app.route("/headers")
def headers():
    """Show HTTP headers for the request."""
    context = {
        "page_title": "App Engine request headers",
        "headers": list(flask.request.headers),
    }

    return flask.render_template("headers.html", **context)


class Anchors(mistune.Renderer):
    """Adds id attributes to <h*> elements."""

    def header(self, text, level, raw=None):
        name = self.choose_name(text)
        class_ = f"title is-{level}"

        return f'<h{level} id="{name}" class="{class_}">{text}</h{level}>'

    def choose_name(self, text):
        text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore")
        text = re.sub(r"[^\w\s-]", "", text.decode("ascii")).strip().lower()
        text = re.sub(r"[-\s]+", "-", text)

        return text
