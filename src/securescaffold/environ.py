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

import functools

import flask


X_APPENGINE_QUEUENAME = "X-Appengine-Queuename"
X_APPENGINE_SCHEDULER = "X-Cloudscheduler"
X_APPENGINE_USER_IS_ADMIN = "X-Appengine-User-Is-Admin"


def admin_only(func):
    """Checks the request is from an App Engine administrator."""

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        request = flask.request

        if is_admin_request(request):
            return func(*args, **kwargs)

        flask.abort(403)

    return _wrapper


def tasks_only(func):
    """Checks the request is from the Tasks scheduler (or an admin).

    This also works for requests from the Tasks scheduler.
    """

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        request = flask.request

        if is_tasks_or_admin_request(request):
            return func(*args, **kwargs)

        flask.abort(403)

    return _wrapper


def is_admin_request(request) -> bool:
    """True if the request was made by a signed-in App Engine administrator."""
    value = request.headers.get(X_APPENGINE_USER_IS_ADMIN)

    return value == "1"


def is_tasks_request(request) -> bool:
    """True if the request is from the Tasks scheduler.

    This also works for requests from the Cron scheduler.
    """
    is_cron_scheduler_request = request.headers.get(X_APPENGINE_QUEUENAME)
    is_task_scheduler_request = request.headers.get(X_APPENGINE_SCHEDULER) == "true"
    
    return bool(is_cron_scheduler_request) or is_task_scheduler_request


def is_tasks_or_admin_request(request) -> bool:
    """True if the request is from the Tasks scheduler (or an admin)."""
    return is_tasks_request(request) or is_admin_request(request)


is_cron_request = is_tasks_request
cron_only = tasks_only
