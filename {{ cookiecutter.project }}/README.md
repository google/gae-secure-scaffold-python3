# {{ cookiecutter.project }}

This is a Secure Scaffold project. More information about Secure Scaffold: https://github.com/davidwtbuxton/gae-secure-scaffold-python/


## Setup

Install the Google Cloud SDK: https://cloud.google.com/sdk/install

After installation, initialize the SDK. You will need to do this before you can deploy your website to App Engine: https://cloud.google.com/sdk/docs/initializing


## Development

When you deploy your website, App Engine will serve all static assets from the "dist" directory. This is controlled by the configuration in "app.yaml". The "app.yaml" configuration also specifies strict Content Security Policy headers (https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP).

The SDK includes `dev_appserver.py` which you can use to run a local development web server.

    dev_appserver.py .

Visit http://localhost:8080 to see your in-development website.


## Deploying to App Engine

The Cloud SDK includes the `gcloud` command-line tool. Use `gcloud` to deploy your website to app Engine:

    gcloud app deploy --project {{ cookiecutter.project }} app.yaml

See the `gcloud` documentation for more information: https://github.com/davidwtbuxton/gae-secure-scaffold-python/

Visit https://{{ cookiecutter.project }}.appspot.com/ to see your website on App Engine. You can switch between deployed versions of your website and delete unused versions with Google Cloud Console: https://console.cloud.google.com/appengine/versions?project={{ cookiecutter.project }}
