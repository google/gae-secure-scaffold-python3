# Secure GAE Scaffold (Python 3)

## Introduction

Please note: this is not an official Google product.

This is a secure scaffold package designed primarily to work with
Google App Engine (although it is not limited to this).

It is built using Python 3 and Flask.

The scaffold provides the following basic security guarantees by default through
a flask app factory found in `secure_scaffold/factories.py`. This app will:

1. Set assorted security headers (Strict-Transport-Security, X-Frame-Options,
   X-XSS-Protection, X-Content-Type-Options, Content-Security-Policy) with
   strong default values to help avoid attacks like Cross-Site Scripting (XSS)
   and Cross-Site Script Inclusion.  See  `add_csp_headers` and
   `settings.CSP_CONFIG`.
1. Verify XSRF tokens by default on authenticated requests using any verb other
   that GET, HEAD, or OPTIONS.  See the `secure_scaffold/xsrf.py` for more information.

## Usage

### Installation

As this is currently in beta we have a beta pypi package.

This project can be installed via

`pip install toaster-secure-scaffold-rc`

For your convenience we also have the option to install with various other
dependencies for the contrib APIs such as cloud-tasks.

These can be included with the `[]` syntax. For example all of them can be installed
via:

`pip install toaster-secure-scaffold-rc[tasks]`


### Starting a new project

Install the Cookiecutter utility. Then create a new empty project:

    pip install cookiecutter
    cookiecutter https://github.com/davidwtbuxton/gae-secure-scaffold-python.git --checkout py37-scaffold

This prompts for the App Engine project name and creates a directory with that name. Inside the directory is the skeleton of a basic app for Python 3 on App Engine standard.


### App Factory

To use the secure scaffold in your app, use our app generator.

```python
from secure_scaffold import factories

app = factories.AppFactory().generate()
```

This will automatically set all the needed CSP headers.


### XSRF

To enable XSRF protection add the decorator to the endpoints you need it for.
This needs to be set *after* the route decorator
e.g.

```python
from secure_scaffold import factories
from secure_scaffold import xsrf

app = factories.AppFactory().generate()

@app.route('/', methods=['GET', 'POST'])
@xsrf.xsrf_protected()
def index():
    return 'Hello World!'
```


We use Flask Sessions for XSRF, for this you should set up a unique Secret Key for your application.

A random one is set in the app factory, but you should overwrite this yourself, see [Flask Sessions](http://flask.pocoo.org/docs/1.0/quickstart/#sessions)


### Configuring Flask and the SECRET_KEY setting

Set the environment variable FLASK_SETTINGS_MODULE to the dotted path name of a Python module. Configuration defaults are loaded from "secure_scaffold.settings". The configuration is loaded when you create the Flask application.

To customize settings, create a Python module that overrides the default settings, and point FLASK_SETTINGS_MODULE to the module name. For example, here's how you can change the name for the session cookie created by Flask:

    # myappconfig.py
    SESSION_COOKIE_NAME = 'myapp_session'

Then set the FLASK_SETTINGS_MODULE:

    # app.yaml
    runtime: python37

    env_variables:
      FLASK_SETTINGS_MODULE = "myappconfig"

The SECRET_KEY setting is read from the datastore when the application starts. If there is no setting, a random key is created and saved.


### Authentication

The Secure Scaffold provides two methods of authentication. One is an in built
authentication system relying on Googles OAuth2 system. The alternative is a system relying on IAP

#### OAuth2 Users

Second generation App Engine systems have had the Users API removed so the majority of
the original functionality isn't available. As a result it is now recommended to use
separate systems such as Googles OAuth2. The Secure Scaffold provides a wrapper for this
based heavily on [this guide](https://developers.google.com/identity/sign-in/web/sign-in).

For this to work there is some minimal setup.

The first is to provide an OAuth Client ID. To do this go to the GCloud console and create
an OAuth Client ID [here](https://console.cloud.google.com/apis/credentials). Ensure you add
the domains you are using to the `Authorised JavaScript Origins` and `Authorised redirect URIs`.
You can include `localhost:5000` in these to enable using this system in development.

Once you have a `Client ID` add it to your settings file like so:

```python
AUTH_OAUTH_CLIENT_ID = 'my-client-id'
```

Once done all that is required is to register the auth blueprint to your project like so:

```python
from secure_scaffold import factories
from secure_scaffold.contrib.users.auth import auth_handler


app = factories.AppFactory().generate()
app.register_blueprint(auth_handler.blueprint)
```

This creates two enpoints at `/auth/login` and `/auth/authenticate`. Login provides a frontend
with a Google sign in button. This sends an API request to `/auth/authenticate` which validates
the login procedure and returns an endpoint to redirect to. By default this is `/`.

If you want to force a user to be logged in to access a URL you can use the provided
`requires_login` decorator like so:

```python
from secure_scaffold import factories
from secure_scaffold.contrib.users.auth import auth_handler


app = factories.AppFactory().generate()
app.register_blueprint(auth_handler.blueprint)


@app.route('/')
@auth_handler.requires_login
def private_view():
    return "You can't see this unless you are logged in."
```

If a user is logged in they will be able to see the page. If they are not they will
automatically be redirected to `/auth/login`.

##### Extending the OAuth2 system.

The OAuth2 system is built using a class at `secure_scaffold.contrib.users.auth.AuthHandler`.

This class is designed to be easy to subclass and override. For instance if you wanted to
change the URL which the user is redirected to on logging in you can do it like so:

```python
from secure_scaffold import factories
from secure_scaffold.contrib.users.auth import AuthHandler

app = factories.AppFactory().generate()

class MyAuthHandler(AuthHandler):
    redirect_url = '/after-login'

auth_handler = MyAuthHandler()
app.register_blueprint(auth_handler.blueprint)
```

#### IAP Users

This is available at `secure_scaffold.contrib.appengine.users`. It provides a `User`
class which has a few useful methods providing the details of the current user.
It also provides `requires_auth` and `requires_admin` decorators which enforce the need
for authentication and admin rights respectively on the views they are applied to.

These work almost identically to how they do in the first generation App Engine APIs.

To use these you will need to enable IAP on your App Engine instance. This is
provides the app with the correct headers for this functionality.


### Tasks

The Secure Scaffold comes with a system for setting up tasks with
[Google Cloud Tasks](https://cloud.google.com/tasks/).

This system works by creating a `TaskRunner` class instance and registering functions
as `Task` objects using a decorator provided by the `TaskRunner` instance.

This creates a view in a [Flask blueprint](http://flask.pocoo.org/docs/dev/blueprints/)
stored in the `TaskRunner` instance and adds a `delay` method to the registered
function - allowing the function to be run later by the task queue.


#### Setup

For this module to work you must first install `google-cloud-tasks`:

    pip install google-cloud-tasks

You must also add a `CLOUD_TASKS_QUEUE_CONFIG` object to your settings file.
It should look like this:

```python
CLOUD_TASKS_QUEUE_CONFIG = {
    'project': 'YOUR GCLOUD PROJECT NAME',
    'location': 'YOUR TASKE QUEUE LOCATION',
    'queue': 'YOUR TASK QUEUE NAME'
}
```

#### Using

A basic example of the task system is as follows:

```python
from flask import request

from secure_scaffold import factories
from secure_scaffold.contrib.cloud_tasks import tasks


app = factories.AppFactory().generate()

task_runner = tasks.TaskRunner('tasks', __name__, url_prefix='/tasks')

app.register_blueprint(task_runner.blueprint)


@task_runner.task(route='/print_task', methods=['POST'])
def print_task():
    arg = request.json().get('arg')
    print(arg)
    return 'OK'


@app.route('/')
def main():
    print_task.delay(arg='Hello, World!')
    return 'OK'
```

This sets up a Secure Scaffold app as well as a task runner. It then registers
the blueprint of the task runner in the app.

We create a task function, which gets an argument called `arg` from
the global `request` object and prints it. This is registered as a task
using the `task_runner.task` decorator.

Finally we create a flask route called `main` which calls the `delay` method
of our task.

Behind the scenes what happens is our `task_runner` creates a `Task` object
containing this function and a `delay` method. It then registers the object
as a flask route at `/tasks/print_task/`. The `Task` objects delay method
makes a request to the cloud tasks API to create a task for this method in
the queue. It takes any arbitrary arguments and keyword arguments and adds
them to the body of this request - making them accessible via the
`flask.request` global variable within the task.

## Scaffold Development

### Structure:

`secure_scaffold/`
- Top level directory

`secure_scaffold/contrib`
- Contains non-essential but useful libraries.
- Holds several alternatives to App Engine APIs
which are no longer available in second generation instances

`secure_scaffold/tests`
- Tests for the secure scaffold

`secure_scaffold/config.py`
- Similar to django settings set up
- Looks for the "SETTINGS_MODULE" environment variable to be set
- See Settings Config below on how to use this

`secure_scaffold/factories.py`
- The main Flask app factory that applies the security defaults
- See App Factory below on how to use this

`secure_scaffold/settings.py`
- Security settings
- Defines our CSP headers and other specifics

`secure_scaffold/xsrf.py`
- Defines XSRF decorators to be used with your flask app
- See XSRF below on how to use this

### Dependency Setup

We recommend setting up a virtual env to install dependencies:

`virtualenv env --python=python3`

`source env/bin/activate`

`pip install -r dev_requirements.txt`

There are some extra dependencies required for the development on specific submodules.

These include:

- `google-cloud-tasks` for development on `secure_scaffold.contrib.cloud_tasks.tasks`


### Testing

To run tests:

    pytest


## Third Party Credits

- Flask
