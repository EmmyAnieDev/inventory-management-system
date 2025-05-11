import os
import sys
from celery import Celery
from config import config

# Add the project directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

celery = Celery(
    'inventory_management',
    broker=config.CELERY_BROKER_URL,
    backend=config.CELERY_RESULT_BACKEND
)

# 👇 Import your tasks so Celery can discover them
import app.tasks.send_email_task

# Configure Celery
celery.conf.update(
    result_expires=3600,
    task_acks_late=True,
    worker_prefetch_multiplier=1
)

if __name__ == '__main__':
    celery.start()
