# Secure GAE Scaffold

## Introduction

Please note: this is not an official Google product.

This is the secure scaffold for Google App Engine.

It is built using Python 3 and Flask.

Structure:

* / - top level directory for common files, e.g. app.yaml

The scaffold provides the following basic security guarantees by default through
a flask app factory found in `secure_scaffold/factories.py`. This app will:

1. Set assorted security headers (Strict-Transport-Security, X-Frame-Options,
   X-XSS-Protection, X-Content-Type-Options, Content-Security-Policy) with
   strong default values to help avoid attacks like Cross-Site Scripting (XSS)
   and Cross-Site Script Inclusion.  See  `add_csp_headers` and
   `settings.CSP_CONFIG`.
1. Verify XSRF tokens by default on authenticated requests using any verb other
   that GET, HEAD, or OPTIONS.  See the `secure_scaffold/xsrf.py` for more information.


## App Factory

To use the secure scaffold in your app, use our app generator.

    from secure_scaffold import factories
    
    app = factories.AppFactory().generate()
    
This will automatically set all the needed CSP headers.

## XSRF

To enable XSRF protection add the decorator to the endpoints you need it for.
This needs to be set *after* the route decorator
e.g.

    @app.route('/', methods=['GET', 'POST'])
    @xsrf.xsrf_protected
    def index():
        return 'Hello World!'


## Settings Config

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


## Scaffold Development
----

### Dependency Setup

We recommend setting up a virtual env to install dependencies:

`virtualenv env --python=python3`

`source env/bin/activate`

`pip install -r dev_requirements.txt`

### Testing

To run unit tests:

`pytest`

