import logging
from flask_mail import Message

from app.extensions import mail
from celery_worker import celery

logger = logging.getLogger(__name__)

@celery.task(name="send_async_email")
def send_async_email(subject, sender, recipients, body):
    """Background task to send an email with Flask-Mail."""

    from app import create_app

    app = create_app()

    with app.app_context():
        try:
            msg = Message(
                subject=subject,
                sender=sender,
                recipients=recipients if isinstance(recipients, list) else [recipients]
            )
            msg.body = body
            mail.send(msg)
            logger.info(f"Email sent successfully to {recipients}")
            return "Email sent successfully!"
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return f"Failed to send email: {str(e)}"
