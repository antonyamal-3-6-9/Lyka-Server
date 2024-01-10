from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lyka.settings')

app = Celery('Lyka')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'adding_task': {
        'task': 'lyka_order.tasks.updating_order',
        'schedule': 100, 
    },
    #     'printingTask': {
    #     'task': 'lyka_order.tasks.printingTask',
    #     'schedule': 900000, 
    # },
}
app.conf.broker_connection_retry_on_startup = True


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))