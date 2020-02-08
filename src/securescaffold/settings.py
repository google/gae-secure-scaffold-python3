import datetime

import flask_talisman


# These control flask-talisman.
CSP_POLICY = flask_talisman.GOOGLE_CSP_POLICY
CSP_POLICY_NONCE_IN = None
CSP_POLICY_REPORT_URI = None
CSP_POLICY_REPORT_ONLY = None

# These control flask-seasurf.
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_TIMEOUT = datetime.timedelta(days=1)
