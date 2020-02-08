#!/bin/bash
set -o errexit -o nounset

PROJECT="python-app"
FLASK_ENV="development"
FLASK_APP="main:app"


# Set --host-port to work around bug with NDB unable to connect to ::1.
gcloud beta emulators datastore start \
    --project "$PROJECT" \
    --host-port localhost \
    &

sleep 5
$(gcloud beta emulators datastore env-init)

# Start your local development server.
export FLASK_SETTINGS_FILENAME="settings.py"
FLASK_ENV="$FLASK_ENV" FLASK_APP="$FLASK_APP" flask run

# Clean up the datastore emulator.
curl --silent -X POST "$DATASTORE_HOST/shutdown"
