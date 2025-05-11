import logging
from app.api.utils.send_mail import schedule_email

logger = logging.getLogger(__name__)

class EmailService:

    @staticmethod
    def send_welcome_email(user, first_name):
        """Schedules a welcome email for the new user."""
        try:
            subject = "Welcome to Our Platform!"
            recipients = [user.email]
            body = (
                f"Hi {first_name},\n\n"
                f"Thank you for registering as a {user.role}.\n\n"
                f"Enjoy your experience with us!\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Welcome email scheduled for: {user.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule welcome email: {str(e)}")

    @staticmethod
    def send_profile_update_email(name, email):
        """Schedules an email to notify the user of a profile update."""
        try:
            subject = "Profile Updated"
            recipients = [email]
            body = (
                f"Dear {name},\n\n"
                f"Your profile has been updated successfully.\n\n"
                f"If you did not make this change, please contact support.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Profile update email scheduled for: {email}")
        except Exception as e:
            logger.warning(f"Failed to schedule profile update email: {str(e)}")

    @staticmethod
    def send_account_deletion_email(name, email):
        """Schedules an email to notify the user of account deletion."""
        try:
            subject = "Account Deleted"
            recipients = [email]
            body = (
                f"Dear {name},\n\n"
                f"Your account has been deleted successfully.\n\n"
                f"We’re sorry to see you go. If this was a mistake, please reach out to us.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Account deletion email scheduled for: {email}")
        except Exception as e:
            logger.warning(f"Failed to schedule account deletion email: {str(e)}")
