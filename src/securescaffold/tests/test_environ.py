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
