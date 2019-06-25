import json
import logging
import os
from typing import Callable

from flask import Blueprint
try:
    from google.cloud import tasks_v2
except ImportError:
    raise ImportError(
        "The secure_scaffold.contrib.cloud_tasks.tasks module currently "
        "requires google-cloud-tasks to run. Please ensure it is installed."
    )
from secure_scaffold import config

logger = logging.getLogger(__file__)


TASK_CLIENT = tasks_v2.CloudTasksClient()


class Task:
    """
    A callable Task object which acts as a standard function
    with the additional `delay` method to allow delayed calling
    of the function by a task runner.

    This is done by taking the function and saving it as an instance attribute.
    If an attempt to use the instance as a callable is made, it automatically
    calls the stored function.

    Otherwise if the `delay` method is called, it creates a task for the function
    with the given keyword arguments.
    """

    QUEUE_SETTINGS_NAME = 'CLOUD_TASKS_QUEUE_CONFIG'

    def __init__(self, func: Callable, route: str):
        """
        Take in the required function and store it.

        Take in the URL route to this function as a view and store it.

        Change the name of the instance to the name of the function to trick
        Flask into not thinking we have duplicated names.

        :param func: The function to be called.
        :param str route: The route to call the function with as a task.
        """
        # Flask needs unique names for each view registered. By taking on
        # the functions name instead of its own (which would be "Task") we
        # allow for Flask to understand this system better.
        self.__name__ = func.__name__  # Help Flask understand this.
        self._func = func
        self.route = route
        self.queue = self.get_task_queue()

    def get_task_queue(self):
        """
        Generate a queue object to create tasks with.

        This is meant as an easy way to override the method for generating
        a queue object for which we make tasks with.
        """

        try:
            queue_settings = config.get_setting(self.QUEUE_SETTINGS_NAME)
        except AttributeError:
            raise AttributeError(
                f"{self.QUEUE_SETTINGS_NAME} setting not defined. "
                f"For {self.__module__}.{self.__name__} to work the "
                f"{self.QUEUE_SETTINGS_NAME} setting must be defined."
            )

        return TASK_CLIENT.queue_path(
            **queue_settings
        )

    def get_base_task(self) -> dict:
        """
        Generate the base task body.

        This method is provided as a convenient way of overriding the
        default body if it requires more complexity than updating a
        setting. The default assumes this is being run in App Engine.

        This body is supposed to be updated later with the task payload
        and URI.

        :return: The base task body.
        """
        return config.get_setting("CLOUD_TASKS_BODY")

    def generate_task_body(self, uri: str, payload: str):
        """
        Generate the full task body.

        Get the base task body and update it with the URI and payload
        of the task being requested.

        :param uri: The URI the task is situated at.
        :param payload: The arguments to be passed to the task.
        """
        task = self.get_base_task()
        task["app_engine_http_request"]["relative_uri"] = uri

        if payload is not None:
            # The API expects a payload of type bytes.
            converted_payload = payload.encode()
            task['app_engine_http_request']['body'] = converted_payload

        return task

    def create_task(self, uri: str, payload: str):
        """
        Create a Cloud Task using global settings

        :param uri: Relative uri to post the task to
        :param payload: String of HTTP request body
        :return: Name of created task
        """
        task = self.generate_task_body(uri, payload)

        logger.info(f"Setting up task with payload {task}")

        # Use the client to build and send the task.
        response = TASK_CLIENT.create_task(self.queue, task)

        return response

    def delay(self, **kwargs):
        """
        Create a task in the task queue system to be run later with
        the given key word arguments.

        :param dict kwargs: The arguments to pass to the function
        """
        logger.info(f'Scheduling task {self._func.__name__} at route {self.route}.')
        return self.create_task(self.route, json.dumps(kwargs))

    def __call__(self, *args, **kwargs):
        """
        Call the stored function as if the instance was the function itself.
        """
        return self._func(*args, **kwargs)


class TaskRunner:
    """
    An object which manages tasks under a Flask Blueprint.

    This generates a Flask Blueprint with the given arguments.

    This allows us to make a decorator which takes a function and adds it
    to a flask endpoint - enabling us to track the endpoints and register
    them as tasks.
    """

    task_class = Task

    def __init__(self, name: str, *args, url_prefix: str = '/tasks', **kwargs):
        """
        Take all the arguments required for a Flask Blueprint, store the
        url_prefix locally so we can use it for telling the tasks which
        endpoint they're stored at.
        """
        self.url_prefix = url_prefix
        self.blueprint = Blueprint(
            name,
            *args,
            url_prefix=url_prefix,
            **kwargs
        )

    def _generate_path(self, route: str) -> str:
        """
        Using the given route and the URL prefix generate the path a task
        will use.
        """
        return os.path.join(self.url_prefix, route)

    def task(self, route: str = None, methods: tuple = ('POST',), **kwargs) -> Callable:
        """
        Decorator generator to create a task and add it to the task runner blueprint.

        :param str route: The URL the task will be under - default to the function name.
        :param tuple methods: The HTTP methods allowed for the route.
        :param kwargs: Other arguments for the route.
        """
        def wrapper(func):
            nonlocal route
            if route is None:
                route = func.__name__
            task = self.task_class(func, self._generate_path(route))
            decorator = self.blueprint.route(route, methods=methods, **kwargs)
            return decorator(task)
        return wrapper
