from celery_worker import celery
from config import config
import logging

logger = logging.getLogger(__name__)

def schedule_email(subject, recipients, body):
    """Schedules an email to be sent using Celery."""
    try:
        task = celery.send_task(
            'send_async_email',
            kwargs={
                'subject': subject,
                'sender': config.MAIL_FROM_NAME,
                'recipients': recipients,
                'body': body
            }
        )
        logger.info(f"Email scheduled: {task.id}")
        return task.id
    except Exception as e:
        logger.error(f"Failed to schedule email: {str(e)}")
        raise
