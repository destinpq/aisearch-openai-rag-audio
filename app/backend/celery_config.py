"""
Celery configuration for background tasks.
"""

import os
from celery import Celery

# Create Celery app
app = Celery('voicerag')

# Configure Celery
app.conf.update(
    broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    worker_max_tasks_per_child=100,
)

# Import tasks modules
app.autodiscover_tasks(['document_processing'])

if __name__ == '__main__':
    app.start() 