from app.api.db import db
from app.api.v1.models.customer import Customer
from app.api.v1.models.user import User
from app.api.v1.schemas.customer import CustomerSchema
from marshmallow import ValidationError
from flask_mail import Message
from app import mail
import logging

from app.api.v1.services.send_mail import EmailService

logger = logging.getLogger(__name__)

class CustomerService:
    @staticmethod
    def get_all_customers(page, per_page, role):
        """Retrieve all customers (admin only) with pagination."""
        if role != 'admin':
            logger.warning("Non-admin user attempted to access all customers")
            raise PermissionError("Access denied. Admin privileges required")

        customers = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
        schema = CustomerSchema(many=True)
        result = {
            "items": schema.dump(customers.items),
            "pagination": {
                "page": customers.page,
                "per_page": customers.per_page,
                "total_pages": customers.pages,
                "total_items": customers.total
            }
        }
        logger.info(f"Retrieved {len(customers.items)} customers (page {page}/{customers.pages})")
        return result

    @staticmethod
    def get_customer(customer_id, user_id, role):
        """Retrieve a customer by ID with access control."""
        customer = Customer.get_by_id(customer_id)
        if not customer:
            logger.warning(f"Customer with ID {customer_id} not found")
            raise ValueError("Customer not found")

        if role != 'admin' and user_id != customer.user_id:
            logger.warning(f"Access denied: User {user_id} tried to access customer {customer_id}")
            raise PermissionError("Access denied")

        schema = CustomerSchema()
        logger.info(f"Customer retrieved: {customer.email} (ID: {customer_id})")
        return schema.dump(customer)

    @staticmethod
    def update_customer(customer_id, user_id, role, data):
        """Update a customer profile with access control."""
        customer = Customer.get_by_id(customer_id)
        if not customer:
            logger.warning(f"Customer with ID {customer_id} not found")
            raise ValueError("Customer not found")

        if role != 'admin' and user_id != customer.user_id:
            logger.warning(f"Access denied: User {user_id} tried to update customer {customer_id}")
            raise PermissionError("Access denied")

        schema = CustomerSchema(partial=True)
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValidationError(f"Invalid input: {str(e)}")

        user = User.get_by_id(customer.user_id)
        for key, value in validated_data.items():
            setattr(customer, key, value)
            if key == 'email' and user:
                setattr(user, key, value)

        customer.save()
        if user:
            user.save()
        logger.info(f"Customer updated: {customer.email} (ID: {customer_id})")

        # Send update confirmation email
        EmailService.send_profile_update_email(customer.first_name, customer.email)

        return schema.dump(customer)

    @staticmethod
    def delete_customer(customer_id, user_id, role):
        """Delete a customer with access control."""
        customer = Customer.get_by_id(customer_id)
        if not customer:
            logger.warning(f"Customer with ID {customer_id} not found")
            raise ValueError("Customer not found")

        if role != 'admin' and user_id != customer.user_id:
            logger.warning(f"Access denied: User {user_id} tried to delete customer {customer_id}")
            raise PermissionError("Access denied")

        customer_email = customer.email

        db.session.delete(customer)
        db.session.commit()
        logger.info(f"Customer deleted: {customer_email} (ID: {customer_id})")

        # Send deletion notification email
        EmailService.send_account_deletion_email(customer.first_name, customer.email)