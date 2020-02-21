# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import traceback

import flask
import google.auth
import google.auth.transport.requests
import requests
import securescaffold
from google.auth.compute_engine import credentials
from google.cloud import storage
from google.oauth2 import service_account


app = securescaffold.create_app(__name__)
_DEFAULT_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'


def in_production():
    return os.getenv('GAE_ENV', '').startswith('standard')


def new_creds(scopes=None):
    """Create credentials wih non-default scopes.

    The IAP API must be enabled, and the service account must have been
    granted permissions to create auth tokens (included in the Service Account
    Token Creator role).
    """
    if not in_production():
        # Local development.
        creds, _ = google.auth.default(scopes=scopes)
        return creds

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
    """List the Google Cloud Storage buckets."""
    # In fact the regular service account token is sufficient to list buckets,
    # but imagine there were other scopes you wanted to use with the default
    # service account.
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
