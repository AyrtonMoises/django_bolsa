from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')

app = Celery('setup')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.task_routes = [
    {'acoes.tasks.*': {'queue': 'fila_padrao'}},

]
app.conf.beat_schedule = {
    'chama_schedule1': {
        'task': 'acoes.tasks.task_scrap_acoes_dia_anterior',
        'schedule': crontab(hour=11, minute=0, day_of_week='1-5'),
        'args': ()
    },
}