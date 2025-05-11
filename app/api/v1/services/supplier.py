from app.api.db import db
from app.api.v1.models.supplier import Supplier
from app.api.v1.models.user import User
from app.api.v1.schemas.supplier import SupplierSchema
from marshmallow import ValidationError
from flask_mail import Message
from app import mail
import logging

from app.api.v1.services.send_mail import EmailService

logger = logging.getLogger(__name__)

class SupplierService:
    @staticmethod
    def get_all_suppliers(page, per_page, role):
        """Retrieve all suppliers (admin only) with pagination."""
        if role != 'admin':
            logger.warning("Non-admin user attempted to access all suppliers")
            raise PermissionError("Access denied. Admin privileges required")

        suppliers = Supplier.query.paginate(page=page, per_page=per_page, error_out=False)
        schema = SupplierSchema(many=True)
        result = {
            "items": schema.dump(suppliers.items),
            "pagination": {
                "page": suppliers.page,
                "per_page": suppliers.per_page,
                "total_pages": suppliers.pages,
                "total_items": suppliers.total
            }
        }
        logger.info(f"Retrieved {len(suppliers.items)} suppliers (page {page}/{suppliers.pages})")
        return result

    @staticmethod
    def get_supplier(supplier_id, user_id, role):
        """Retrieve a supplier by ID with access control."""
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            logger.warning(f"Supplier with ID {supplier_id} not found")
            raise ValueError("Supplier not found")

        if role != 'admin' and user_id != supplier.user_id:
            logger.warning(f"Access denied: User {user_id} tried to access supplier {supplier_id}")
            raise PermissionError("Access denied")

        schema = SupplierSchema()
        logger.info(f"Supplier retrieved: {supplier.email} (ID: {supplier_id})")
        return schema.dump(supplier)

    @staticmethod
    def update_supplier(supplier_id, user_id, role, data):
        """Update a supplier profile with access control."""
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            logger.warning(f"Supplier with ID {supplier_id} not found")
            raise ValueError("Supplier not found")

        if role != 'admin' and user_id != supplier.user_id:
            logger.warning(f"Access denied: User {user_id} tried to update supplier {supplier_id}")
            raise PermissionError("Access denied")

        schema = SupplierSchema(partial=True)
        try:
            validated_data = schema.load(data)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise ValidationError(f"Invalid input: {str(e)}")

        user = User.get_by_id(supplier.user_id)
        for key, value in validated_data.items():
            setattr(supplier, key, value)
            if key == 'email' and user:
                setattr(user, key, value)

        supplier.save()
        if user:
            user.save()
        logger.info(f"Supplier updated: {supplier.email} (ID: {supplier_id})")

        # Send update confirmation email
        EmailService.send_account_deletion_email(supplier.first_name, supplier.email)

        return schema.dump(supplier)

    @staticmethod
    def delete_supplier(supplier_id, user_id, role):
        """Delete a supplier with access control."""
        supplier = Supplier.get_by_id(supplier_id)
        if not supplier:
            logger.warning(f"Supplier with ID {supplier_id} not found")
            raise ValueError("Supplier not found")

        if role != 'admin' and user_id != supplier.user_id:
            logger.warning(f"Access denied: User {user_id} tried to delete supplier {supplier_id}")
            raise PermissionError("Access denied")

        supplier_email = supplier.email

        db.session.delete(supplier)
        db.session.commit()
        logger.info(f"Supplier deleted: {supplier_email} (ID: {supplier_id})")

        # Send deletion notification email
        EmailService.send_account_deletion_email(supplier.first_name, supplier.email)