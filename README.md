# Secure GAE Scaffold

## Introduction

Please note: this is not an official Google product.

This is the secure scaffold package for Google App Engine.

It is built using Python 3 and Flask.

Structure:

`secure_scaffold/` 
- Top level directory

`secure_scaffold/contrib` 
- Contains shims for App Engine APIs that are no longer available in Python 3

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

    from secure_scaffold import factories
    
    app = factories.AppFactory().generate()
    
This will automatically set all the needed CSP headers.

### XSRF

To enable XSRF protection add the decorator to the endpoints you need it for.
This needs to be set *after* the route decorator
e.g.

    @app.route('/', methods=['GET', 'POST'])
    @xsrf.xsrf_protected
    def index():
        return 'Hello World!'


### Settings Config

Similar to django settings, to enable multiple settings files you need to set an environment variable.
Your folder structure should include a settings folder containing your settings files, for example:
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

### Dependency Setup

We recommend setting up a virtual env to install dependencies:

`virtualenv env --python=python3`

`source env/bin/activate`

`pip install -r dev_requirements.txt`

### Testing

To run unit tests:

`pytest`

