# Variables with all-capitals will be added to the Flask app's configuration.

# See https://github.com/GoogleCloudPlatform/flask-talisman for details on
# configuring CSP.

# Strict policy, allows using nonce in templates to load JS and CSS assets.
CSP_POLICY = {
    "default-src": "'none'",
    "script-src": "",
    "style-src": "",
}
CSP_POLICY_NONCE_IN = ["script-src", "style-src"]
