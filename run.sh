#!/bin/bash
# Copyright 2025 Community Calendar
#
# Local development server script

# Start the Cloud Datastore Emulator
echo "Starting Cloud Datastore Emulator..."
gcloud beta emulators datastore start --no-store-on-disk --consistency=1.0 --host-port=localhost:8081 &
DATASTORE_PID=$!

# Wait for emulator to start
sleep 3

# Set environment variables for the emulator
$(gcloud beta emulators datastore env-init)

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Run the Flask development server
echo "Starting Flask development server..."
export DATASTORE_EMULATOR_HOST=localhost:8081
export DATASTORE_PROJECT_ID=community-calendar-dev
python main.py

# Cleanup: kill the datastore emulator when Flask server stops
kill $DATASTORE_PID
