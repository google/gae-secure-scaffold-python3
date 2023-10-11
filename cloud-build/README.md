Cloud build image
=================

The Cloud Build trigger uses a custom image saved to the project's container registry. This image has executables for Python versions 3.7 and 3.8.

Use the files in this directory to create or update the custom image.


Build
-----

    cd cloud-build
    gcloud builds submit \
        --project gae-secure-scaffold-python3 \
        --config cloudbuild.yaml


The Docker image is based on https://github.com/dhermes/python-multi


Continuous integration
----------------------

The CI pipeline uses the Cloud Build GitHub app, and a Cloud Build trigger configured to fire when pull requests are made.

Cloud Build dashboard: https://console.cloud.google.com/cloud-build/dashboard?project=gae-secure-scaffold-python3
