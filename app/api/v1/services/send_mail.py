import logging
from app.api.utils.send_mail import schedule_email

logger = logging.getLogger(__name__)


class EmailService:

    @staticmethod
    def send_welcome_email(user, first_name):
        """Schedules a welcome email for the new user.

        Args:
            user (User): The user object containing email and role.
            first_name (str): The first name of the user.

        Returns:
            None
        """
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
        """Schedules an email to notify the user of a profile update.

        Args:
            name (str): The name of the user.
            email (str): The email address of the user.

        Returns:
            None
        """
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
        """Schedules an email to notify the user of account deletion.

        Args:
            name (str): The name of the user.
            email (str): The email address of the user.

        Returns:
            None
        """
        try:
            subject = "Account Deleted"
            recipients = [email]
            body = (
                f"Dear {name},\n\n"
                f"Your account has been deleted successfully.\n\n"
                f"We're sorry to see you go. If this was a mistake, please reach out to us.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Account deletion email scheduled for: {email}")
        except Exception as e:
            logger.warning(f"Failed to schedule account deletion email: {str(e)}")


    @staticmethod
    def send_incoming_order_created_email(supplier, product, order):
        """Schedules an email to notify the supplier of a new incoming order.

        Args:
            supplier (Supplier): The supplier object.
            product (Product): The product object.
            order (IncomingOrder): The incoming order object.

        Returns:
            None
        """
        try:
            subject = "Incoming Order Created"
            recipients = [supplier.email]
            body = (
                f"Dear {supplier.first_name},\n\n"
                f"Your incoming order for {product.name} (Quantity: {order.quantity_supply}) "
                f"has been created successfully.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Incoming order creation email scheduled for: {supplier.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule incoming order creation email: {str(e)}")


    @staticmethod
    def send_incoming_order_updated_email(supplier, product, order):
        """Schedules an email to notify the supplier of an updated incoming order.

        Args:
            supplier (Supplier): The supplier object.
            product (Product): The product object.
            order (IncomingOrder): The incoming order object.

        Returns:
            None
        """
        try:
            subject = "Incoming Order Updated"
            recipients = [supplier.email]
            body = (
                f"Dear {supplier.first_name},\n\n"
                f"Your incoming order for {product.name} (Quantity: {order.quantity_supply}) "
                f"has been updated successfully.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Incoming order update email scheduled for: {supplier.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule incoming order update email: {str(e)}")


    @staticmethod
    def send_incoming_order_deleted_email(supplier, product, quantity):
        """Schedules an email to notify the supplier of a deleted incoming order.

        Args:
            supplier (Supplier): The supplier object.
            product (Product): The product object.
            quantity (int): The quantity that was in the deleted order.

        Returns:
            None
        """
        try:
            subject = "Incoming Order Deleted"
            recipients = [supplier.email]
            body = (
                f"Dear {supplier.first_name},\n\n"
                f"An incoming order for {product.name} (Quantity: {quantity}) "
                f"has been deleted.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Incoming order deletion email scheduled for: {supplier.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule incoming order deletion email: {str(e)}")


    @staticmethod
    def send_outgoing_order_created_email(customer, product, order):
        """Schedules an email to notify the customer of a new placed order.

        Args:
            customer (Customer): The customer object.
            product (Product): The product object.
            order (OutgoingOrder): The outgoing order object.

        Returns:
            None
        """
        try:
            subject = "Outgoing Order Created"
            recipients = [customer.email]
            body = (
                f"Dear {customer.first_name},\n\n"
                f"Your order for {product.name} (Quantity: {order.quantity_order}) "
                f"has been placed successfully.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Outgoing order creation email scheduled for: {customer.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule outgoing order creation email: {str(e)}")


    @staticmethod
    def send_outgoing_order_updated_email(customer, product, order):
        """Schedules an email to notify the customer of an updated placed order.

        Args:
            customer (Customer): The customer object.
            product (Product): The product object.
            order (OutgoingOrder): The outgoing order object.

        Returns:
            None
        """
        try:
            subject = "Outgoing Order Updated"
            recipients = [customer.email]
            body = (
                f"Dear {customer.first_name},\n\n"
                f"Your order for {product.name} (Quantity: {order.quantity_order}) "
                f"has been updated successfully.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Outgoing order update email scheduled for: {customer.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule outgoing order update email: {str(e)}")


    @staticmethod
    def send_outgoing_order_deleted_email(customer, product, order):
        """Schedules an email to notify the customer of a deleted placed order.

        Args:
            customer (Customer): The customer object.
            product (Product): The product object.
            order (OutgoingOrder): The outgoing order object.

        Returns:
            None
        """
        try:
            subject = "Outgoing Order Deleted"
            recipients = [customer.email]
            body = (
                f"Dear {customer.first_name},\n\n"
                f"Your order for {product.name} (Quantity: {order.quantity_order}) "
                f"has been deleted successfully.\n\n"
                f"- The Team"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Outgoing order delete email scheduled for: {customer.email}")
        except Exception as e:
            logger.warning(f"Failed to schedule outgoing order delete email: {str(e)}")


    @staticmethod
    def send_low_stock_alert_email(admin, product, stock):
        """Schedules an email to notify the admin of low stock for a product.

        Args:
            admin (User): The admin user object.
            product (Product): The product with low stock.
            stock (Stock): The stock object containing available quantity.

        Returns:
            None
        """
        try:
            subject = "Low Stock Alert"
            recipients = [admin.email]
            body = (
                f"Dear Admin,\n\n"
                f"Stock for {product.name} (ID: {product.id}) is low: {stock.available_quantity} units remaining.\n\n"
                f"Please restock as soon as possible.\n\n"
                f"- The Inventory System"
            )
            schedule_email(subject=subject, recipients=recipients, body=body)
            logger.info(f"Low stock alert email scheduled for admin: {admin.email}, product: {product.name}")
        except Exception as e:
            logger.warning(f"Failed to schedule low stock alert email: {str(e)}")