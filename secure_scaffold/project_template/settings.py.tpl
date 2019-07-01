{% if DATABASE_ENGINE %}
DATABASE_SETTINGS = {
    'engine': '{{ DATABASE_ENGINE }}',
    'settings': {
        'project': '{{ GCLOUD_NAME }}'
    }
}
{% endif %}
{% if TASKS %}
CLOUD_TASKS_QUEUE_CONFIG = {
    'project': '{{ GCLOUD_NAME }}',
    'location': '{{ TASK_LOCATION }}',
    'queue': '{{ TASK_QUEUE }}'
}
{% endif %}
