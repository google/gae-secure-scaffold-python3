import traceback

import flask
import google.auth
import google.auth.transport.requests
import requests
from google.auth.compute_engine import credentials
from google.cloud import storage
from google.oauth2 import service_account


app = flask.Flask(__name__)
_DEFAULT_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'


def new_creds(scopes=None):
    request = google.auth.transport.requests.Request()
    creds = credentials.IDTokenCredentials(request, None)
    signer = creds.signer
    service_account_email = creds.service_account_email
    token_uri = _DEFAULT_TOKEN_URI
    creds = service_account.Credentials(signer, service_account_email, token_uri)

    if scopes:
        creds = creds.with_scopes(scopes)

    return creds


@app.route('/')
def home():
    try:
        creds = new_creds()
        client = storage.Client(credentials=creds)
        buckets = [repr(o) for o in client.list_buckets()]
        error = None
    except Exception:
        error = traceback.format_exc()
        buckets = None

    context = {
        'buckets': buckets,
        'error': error,
    }

    return flask.jsonify(context)
