from secure_scaffold import factories
{% if TASKS %}
from tasks import task_runner, example_task
{% endif %}

app = factories.AppFactory().generate()
{% if TASKS %}
app.register_blueprint(task_runner.blueprint)
{% endif %}

@app.route('/')
def home():
    {% if TASKS %}example_task.delay(){% endif %}
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)

