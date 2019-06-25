import json
from unittest import mock

import pytest
from flask import Blueprint

from secure_scaffold.contrib.cloud_tasks import tasks


def get_settings(setting):
    if setting == 'CLOUD_TASKS_QUEUE_CONFIG':
        return {
            'project': 'test',
            'location': 'test',
            'queue': 'test'
        }
    return {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'app_engine_routing': {
                'version': 'default'
            },
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    }


@mock.patch('secure_scaffold.contrib.cloud_tasks.tasks.TASK_CLIENT')
@mock.patch('secure_scaffold.contrib.cloud_tasks.tasks.config')
def test_create_task(mock_config, mock_client):
    mock_config.get_setting = get_settings

    payload = "{'headers': 'Name', 'id: '123'}"
    uri = "/create_spreadsheet"
    path = "testpath"

    task_data = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'app_engine_routing': {
                'version': 'default'
            },
            'relative_uri': uri,
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    }

    mock_client.queue_path.return_value = path

    task = tasks.Task(print, '/test')
    task.create_task(uri, None)

    mock_client.queue_path.assert_called_once_with(
        project='test',
        location='test',
        queue='test'
    )
    mock_client.create_task.assert_called_once_with(
        path,
        task_data
    )


def test_task_raises_attribute_error_no_settings():
    with pytest.raises(AttributeError):
        tasks.Task(print, '/test')


@pytest.mark.parametrize('func,result', (
        (lambda x: x + 1, 6),
        (lambda x: x * 5, 25),
        (lambda x: x ** 3, 125),
))
@mock.patch('secure_scaffold.contrib.cloud_tasks.tasks.config')
def test_task_callable(mock_config, func, result):
    mock_config.get_setting = get_settings
    task = tasks.Task(func, '/test')
    assert task(5) == result


@mock.patch('secure_scaffold.contrib.cloud_tasks.tasks.TASK_CLIENT')
@mock.patch('secure_scaffold.contrib.cloud_tasks.tasks.config')
def test_task_delay(mock_config, mock_client):
    path = "testpath"
    mock_client.queue_path.return_value = path
    mock_config.get_setting = get_settings
    data = {'test': 1, 'another': 'test'}
    uri = "/test"
    task_data = {
        'app_engine_http_request': {  # Specify the type of request.
            'http_method': 'POST',
            'app_engine_routing': {
                'version': 'default'
            },
            'relative_uri': uri,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(data).encode()
        }
    }

    task = tasks.Task(print, uri)

    task.delay(**data)

    mock_client.create_task.assert_called_once_with(
        path,
        task_data
    )


def test_task_runner():
    runner = tasks.TaskRunner('test', 'test', url_prefix='/testing')
    assert runner.url_prefix == '/testing'
    assert isinstance(runner.blueprint, Blueprint)
    assert runner.blueprint.url_prefix == '/testing'


def test_task_runner_generate_path():
    runner = tasks.TaskRunner('test', 'test', url_prefix='/testing')
    assert runner._generate_path('test') == '/testing/test'


@mock.patch('secure_scaffold.contrib.cloud_tasks.tasks.config')
def test_task_runner_generate_task(mock_config):
    mock_config.get_setting = get_settings
    runner = tasks.TaskRunner('test', 'test', url_prefix='/testing')

    @runner.task()
    def task_1():
        return 1

    @runner.task(route='tester')
    def task_2():
        return 2

    assert isinstance(task_1, tasks.Task)
    assert task_1.route == runner._generate_path('task_1')
    assert task_1() == 1

    assert isinstance(task_2, tasks.Task)
    assert task_2.route == runner._generate_path('tester')
    assert task_2() == 2
