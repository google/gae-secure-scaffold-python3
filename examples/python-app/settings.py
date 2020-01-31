# Variables with all-capitals will be added to the Flask app's configuration.

# See https://github.com/GoogleCloudPlatform/flask-talisman for details on
# configuring CSP.
CONTENT_SECURITY_POLICY = {
    "script-src": "'self'",
}
