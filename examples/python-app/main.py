import os

import flask
import secure_scaffold


app = secure_scaffold.create_app(__name__)


@app.route('/')
def home():
    context = {
        'title': '<b>Welcome</b>',
    }
    return flask.render_template('home.html', **context)

# Run your app with python -m flask run
