#!/bin/bash
set -o errexit -o nounset

PROJECT="scaffold-tests"

trap "kill 0" EXIT

# Set --host-port to work around bug with NDB unable to connect to ::1.
gcloud beta emulators datastore start \
    --project "$PROJECT" \
    --no-store-on-disk \
    --consistency=1.0 \
    --host-port localhost \
    &

sleep 5

$(gcloud beta emulators datastore env-init)

pytest

wait
