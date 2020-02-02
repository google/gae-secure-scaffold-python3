import os

import flask
import securescaffold


app = securescaffold.create_app(__name__)


@app.route('/')
def home():
    context = {
        'title': '<b>Welcome</b>',
    }
    return flask.render_template('home.html', **context)

# Run your app with python -m flask run
