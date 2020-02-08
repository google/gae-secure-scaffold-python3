Python application example
==========================

Layout
------

 * `app.yaml` - Configure App Engine to serve your application.
 * `main.py` - The default entry-point for Python applications on App Engine.
 * `requirements.txt` - Third-party libaries that will be installed automatically when you deploy your application.
 * `run.sh` - Helper script to run the datastore emulator and the Flask development server.
 * `settings.py` - Custom settings for your Flask application.


Deployment
----------

    gcloud app deploy --project [YOUR_PROJECT_ID] app.yaml
