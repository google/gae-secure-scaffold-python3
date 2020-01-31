#!/bin/bash
set -o errexit -o nounset

PROJECT="{{ cookiecutter.project }}"
FLASK_ENV="development"
FLASK_APP="main:app"


# Set --host-port to work around bug with NDB unable to connect to ::1.
gcloud beta emulators datastore start \
    --project "$PROJECT" \
    --no-store-on-disk \
    --host-port localhost \
    &

sleep 2
$(gcloud beta emulators datastore env-init)

FLASK_ENV="$FLASK_ENV" FLASK_APP="$FLASK_APP" flask run

# Clean up the datastore emulator.
curl -X POST "$DATASTORE_HOST/shutdown"
