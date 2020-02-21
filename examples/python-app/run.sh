#!/bin/bash
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
