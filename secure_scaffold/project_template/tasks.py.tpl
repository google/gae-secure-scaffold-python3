from secure_scaffold.contrib.cloud_tasks import tasks

task_runner = tasks.TaskRunner('tasks', __name__)


@task_runner.task()
def example_task():
    return 'Hello, Task!'

