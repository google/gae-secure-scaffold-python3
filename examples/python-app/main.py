import flask

from secure_scaffold import factories


app = factories.AppFactory(__name__).generate()


@app.route('/')
def home():
    context = {
        'title': '<b>Welcome</b>',
    }
    return flask.render_template('home.html', **context)

# Run your app with python -m flask run
