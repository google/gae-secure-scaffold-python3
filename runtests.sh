#!/bin/bash
set -o errexit -o nounset

PROJECT="scaffold-tests"

# Set --host-port to work around bug with NDB unable to connect to ::1.
gcloud beta emulators datastore start \
    --project "$PROJECT" \
    --no-store-on-disk \
    --consistency=1.0 \
    --host-port localhost \
    &

sleep 2
$(gcloud beta emulators datastore env-init)

# The actual test runner.
pytest

# Clean up the datastore emulator.
curl -X POST "$DATASTORE_HOST/shutdown"
