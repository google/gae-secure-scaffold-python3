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

import flask

import securescaffold


def test_tasks_only_allowed():
    app = flask.Flask("test")
    app.add_url_rule("/", "home", securescaffold.tasks_only(lambda: ""))

    headers = [("X-Appengine-Queuename", "__cron")]
    response = app.test_client().get("/", headers=headers)

    assert response.status_code == 200


def test_tasks_only_not_allowed():
    app = flask.Flask("test")
    app.add_url_rule("/", "home", securescaffold.tasks_only(lambda: ""))

    headers = []
    response = app.test_client().get("/", headers=headers)

    assert response.status_code == 403


def test_tasks_only_admin_user_allowed():
    app = flask.Flask("test")
    app.add_url_rule("/", "home", securescaffold.tasks_only(lambda: ""))

    headers = [("X-Appengine-User-Is-Admin", "1")]
    response = app.test_client().get("/", headers=headers)

    assert response.status_code == 200


def test_admin_only_allowed():
    app = flask.Flask("test")
    app.add_url_rule("/", "home", securescaffold.admin_only(lambda: ""))

    headers = [("X-Appengine-User-Is-Admin", "1")]
    response = app.test_client().get("/", headers=headers)

    assert response.status_code == 200


def test_admin_only_not_allowed():
    app = flask.Flask("test")
    app.add_url_rule("/", "home", securescaffold.admin_only(lambda: ""))

    headers = [("X-Appengine-User-Is-Admin", "0")]
    response = app.test_client().get("/", headers=headers)

    assert response.status_code == 403
