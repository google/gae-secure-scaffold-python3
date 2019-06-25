# Secure GAE Scaffold (Python 3)

## Introduction

Please note: this is not an official Google product.

This is a secure scaffold package designed primarily to work with
Google App Engine (although it is not limited to this).

It is built using Python 3 and Flask.

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

**coming soon**

`pip install secure_scaffold`

**Not uploaded to PyPi yet so for now**:

` python3 setup.py sdist bdist_wheel `

Copy the `.whl` file into your project and add it into your requirements.txt


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


### Settings Config

Similar to django settings, to enable multiple settings files you need to set an environment variable.
Your folder structure should include a settings folder containing your settings files, for example:

    my_project/
        settings/
            __init__.py
            base.py
            development.py
            production.py
            
You should then set the environment variable (**SETTINGS_MODULE**) to the settings you require in that environment.

    export SETTINGS_MODULE=settings.development
    
You can then import your settings in your project like this:

    from secure_scaffold.config import settings

### Users 

To use the Users class you will need to enable IAP on your App Engine instance. 

This is so App Engine will send the correct headers.


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

### Dependency Setup

We recommend setting up a virtual env to install dependencies:

`virtualenv env --python=python3`

`source env/bin/activate`

`pip install -r dev_requirements.txt`

### Testing

To run unit tests:

`pytest`


## Third Party Credits

- Flask
