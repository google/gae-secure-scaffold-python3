import os

import click
from jinja2 import FileSystemLoader, Environment


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name', metavar='<name>')
@click.argument('gcloud_project', metavar='<gcloud_project>')
@click.option('database',
              '--database',
              prompt="Which database do you want to use?",
              help='Argument to show which, if any, database system is desired.',
              type=click.Choice(['none', 'firestore', 'datastore']),
              show_choices=True)
@click.option('--tasks/--no-tasks',
              default=False,
              help='Flag to show if the google-cloud-tasks system is required')
def start_project(name, gcloud_project, database, tasks):
    """
    This command creates a new project structure under the directory <name>.
    """
    path = os.path.join(os.path.dirname(__file__), 'project_template')
    loader = FileSystemLoader(path)
    env = Environment(loader=loader)

    os.mkdir(os.path.join(os.curdir, name))

    to_render = ['app.yaml', 'main.py',
                 'requirements.txt',
                 'settings.py', 'README.md']

    if database != 'none':
        context = {
            'DATABASE_ENGINE': f'secure_scaffold.contrib.db.engine.{database}',
            'DATABASE_CHOICE': f'{database}',
            'GCLOUD_NAME': gcloud_project,
            'PROJECT_NAME': name,
            'TASKS': tasks,
            'DEPENDENCIES': 1
        }
        to_render.append('models.py')
    else:
        context = {
            'DATABASE_CHOICE': '',
            'TASKS': tasks,
            'DEPENDENCIES': 0,
        }
    if tasks:
        to_render.append('tasks.py')
        context['TASK_QUEUE'] = click.prompt('What is the name of the task queue?')
        context['TASK_LOCATION'] = click.prompt('What region is the task located in?')
        context['DEPENDENCIES'] += 1

    click.secho(f'Generating project structure for {name}', fg='green')

    for file in to_render:
        template = env.get_template(f'{file}.tpl')
        with open(os.path.join(os.curdir, name, file), 'w') as to_write:
            to_write.write(template.render(**context))

    click.secho(f'Project generated in ./{name}. '
                f'Run cd {name} to see the project.', fg='green')


if __name__ == '__main__':
    cli()
