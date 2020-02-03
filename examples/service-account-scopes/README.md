Service account demo
====================

When running on App Engine standard Python 3.7 runtime, you can use `google.auth.default()` to get the default service account credentials. But you cannot use those credentials to obtain additional scopes:

    import google.auth

    extra_scopes = []
    creds, expiry = google.auth.default()
    # This will raise "AttributeError: 'Credentials' object has no attribute 'with_scopes'"
    creds = creds.with_scopes(scopes=extra_scopes)

You can create a JSON file with the secrets, and create credentials using that file, but this is not ideal on App Engine because you will have to deploy the JSON file somehow.

The sample code in this directory shows another way to create credentials with custom scopes. This requires you have enabled the Identiy and Access Management API for your project, and have granted the Service Account Token Creator role to the service account.

Identity and Access Management (IAM) API, https://cloud.google.com/iam/docs/
