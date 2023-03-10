# Secure Scaffold

## Introduction

This is not an officially supported Google product.

Secure Scaffold helps you build websites on [Google's App Engine standard](https://cloud.google.com/appengine/docs/standard/python3/) platform with security features enabled by default. It is designed for both static websites which have no dynamic back-end code, and Python web applications.

The scaffold consists of:

 * A [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for starting a static website project.
 * Examples of App Engine websites: a static-only website; a mostly static website with back-end logic to redirect users depending on the Accept-Language header; a Flask application that uses CSP nonces, CSRF-protected forms, and more security features.
 * A Python library for creating a [Flask](https://flask.palletsprojects.com/) website with secure defaults. This uses the [Flask-SeaSurf](https://github.com/maxcountryman/flask-seasurf) library to enable [CSRF](https://developer.mozilla.org/en-US/docs/Glossary/CSRF) protection, and the [Flask-Talisman](https://github.com/GoogleCloudPlatform/flask-talisman) library to enable [CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP) (Content Security Policy) headers and other security features.


## Using the website template

Secure Scaffold provides a [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template. [Install the Cookiecutter command](https://cookiecutter.readthedocs.io/en/latest/), then create a project from the template - you will be prompted for a project name. Project names must start with a letter and use lower-case letters and numbers and dashes, for example "my-project-1":

    cookiecutter https://github.com/google/gae-secure-scaffold-python3.git

Cookiecutter will create a new folder with your project name. Inside the folder is a configuration for a static website, with instructions for deploying the website to App Engine.


## Website examples

We have included examples of websites that use the Secure Scaffold. We hope you find these useful when building your own websites!

 * A static site - uses app.yaml to serve a home page and all assets from a directory, with HTTPS and secure headers.
 * A mostly-static site which redirects requests depending on the Accept-Language header - uses app.yaml to serve the static assets and configures a root page handler that redirects visitors to `/intl/<code>`.
 * A secure Flask application - uses securescaffold to create an application with secure defaults, and demonstrates how to customise the application and extend it for common uses.


## Using the secure scaffold Python library

### Installation and quick start

Add the library to requirements.txt:

    # requirements.txt
    https://github.com/google/gae-secure-scaffold-python3/archive/master.zip

Better is to pin to a specific tag or revision. For example:

    https://github.com/google/gae-secure-scaffold-python3/archive/1.1.0.zip

Install the library in your Python development environment:

    pip install https://github.com/google/gae-secure-scaffold-python3/archive/master.zip

Import the library and use it to create a Flask application:

    # main.py
    import securescaffold

    app = securescaffold.create_app(__name__)

    @app.route("/")
    def hello():
      return "<h1>Hello</h1>"

The line `app = securescaffold.create_app(__name__)` creates a Flask application which includes the Flask-SeaSurf and Flask-Talisman libraries. It also reads an initial configuration from `securescaffold.settings`.

The included examples show [how to start the datastore emulator and the Flask server for local development](https://github.com/google/gae-secure-scaffold-python3/blob/master/examples/python-app/run.sh) and how to [start and stop the emulator](https://github.com/google/gae-secure-scaffold-python3/blob/master/src/securescaffold/tests/test_factory.py) when writing tests. **N.B. the emulator is for testing and local development only. Do not use it when deploying your application to App Engine.**


### Configuring your application with FLASK_SETTINGS_FILENAME

When you create a Flask app with `app = securescaffold.create_app(__name__)` the configuration is read from `securescaffold.settings` and the filename in the `FLASK_SETTINGS_FILENAME` environment variable (if it exists).

You can customise your application by creating a Python file. Then set the environment variable `FLASK_SETTINGS_FILENAME` to point to your Python file. When your code calls `securescaffold.create_app(__name__)`, your custom configuration will be read from the Python file.

    # Custom settings in "settings.py"
    SESSION_COOKIE_NAME = "my-custom-cookie"

And add the environment variable to `app.yaml`:

    # app.yaml
    runtime: python37

    handlers:
      - url: /.*
        script: auto

    env_variables:
      FLASK_SETTINGS_FILENAME: "settings.py"

See [Configuration Handling](https://flask.palletsprojects.com/en/master/config/) in the Flask documentation for more details.


### Changing the CSP configuration

Secure Scaffold uses Flask-Talisman's Google policy as the default CSP policy. You can customise the CSP policy by adding these variables to your custom configuration:

Configuration name     | Talisman equivalent                 | Default value |
-----------------------|-------------------------------------|---------------|
CSP_POLICY             | content_security_policy             | GOOGLE_CSP_POLICY |
CSP_POLICY_NONCE_IN    | content_security_policy_nonce_in    | None          |
CSP_POLICY_REPORT_URI  | content_security_policy_report_uri  | None          |
CSP_POLICY_REPORT_ONLY | content_security_policy_report_only | None          |

See the [Flask-Talisman documentation](https://github.com/GoogleCloudPlatform/flask-talisman) for details of how to use these settings.


### CSRF protection with Flask-SeaSurf

The Flask-SeaSurf library provides CSRF protection. An instance of `SeaSurf` is assigned to the Flask application as `app.csrf`. You can use this to decorate a request handler as exempt from CSRF protection:

    # main.py
    import securescaffold

    app = securescaffold.create_app(__name__)

    @app.csrf.exempt
    @app.route("/csp-report", methods=["POST"])
    def csp_report():
      """CSP report handlers accept POST requests with no CSRF token."""
      return ""

See the [Flask-SeaSurf documentation](https://flask-seasurf.readthedocs.io/) for details of configuration and use.


### Authenticating users with IAP

App Engine supports [the IAP service](https://cloud.google.com/iap/docs) (Identity-Aware Proxy). When IAP is enabled and configured to require authentication, you can use Secure Scaffold to get the signed-in user's email address. This is equivalent to the Users API that was available with the Python 2.7 runtime, but which is not available on the Python 3 runtime.

    # main.py
    import securescaffold
    from securescaffold.contrib.appengine import users

    app = securescaffold.create_app(__name__)

    @app.route("/")
    def hello():
        user = users.get_current_user()

        if user:
            email = user.email()
            user_id = user.user_id()

            return "Hello signed-in user"

      return "Not signed-in"


### Securing request handlers and cron tasks

**You must decorate a cron request handler with `@securescaffold.cron_only` to prevent unauthorized requests.**

Secure Scaffold (thanks to Flask-Talisman) configures HTTP requests to be redirected to use HTTPS. However [App Engine's cron scheduler](https://cloud.google.com/appengine/docs/standard/python3/scheduling-jobs-with-cron-yaml#validating_cron_requests) will make HTTP requests to your cron request handlers (not HTTPS), and the cron requests will fail if your application tries to redirect the request to use HTTPS.

An instance of `Talisman` is assigned to the Flask application as `app.talisman`. You can use this to allow HTTP requests to a cron request handler.

    # main.py
    import securescaffold

    app = securescaffold.create_app(__name__)

    @app.route("/cron")
    @app.talisman(force_https=False)
    @securescaffold.cron_only
    def cron_task():
        # This request handler is protected by the `securescaffold.cron_only`
        # decorator so will only be called if the request is from the cron
        # scheduler or from an App Engine project admin.
        return ""

Secure Scaffold includes the following decorators to help prevent unauthorised access to your request handlers:

 * `securescaffold.admin_only`
   Checks the request was made by a signed-in App Engine admin. If not, the request receives a 403 forbidden response. N.B. you must restrict access to your website with IAP to allow administrators to sign-in.
 * `securescaffold.cron_only`
   Checks the request was made by the Cron / Tasks scheduler or by a signed-in App Engine admin. If not, the request receives a 403 forbidden response.
 * `securescaffold.tasks_only`
   Same as the `securescaffold.cron_only` decorator.



## Third-party credits

This project is built on other projects. Here are some of them:

 * Flask - https://flask.palletsprojects.com/
 * Flask-SeaSurf - https://github.com/maxcountryman/flask-seasurf
 * Flask-Talisman - https://github.com/GoogleCloudPlatform/flask-talisman
 * `secure_scaffold.contrib.appengine.users` from Toaster - https://github.com/toasterco/gae-secure-scaffold-python
