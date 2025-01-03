from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Using a string here means the worker doesn't need to serialize
# the configuration object to child processes.
# Namespace 'CELERY' means all Celery-related config keys
# should start with 'CELERY_'.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in all installed apps.
app.autodiscover_tasks()

