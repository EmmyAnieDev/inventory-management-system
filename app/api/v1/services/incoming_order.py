from datetime import datetime

from app.api.db import db
from app.api.v1.models.supplier import Supplier
from app.api.v1.models.product import Product
from app.api.v1.models.stock import Stock
from app.api.v1.models.incoming_order import IncomingOrder
from app.api.v1.schemas.incoming_order import IncomingOrderSchema
from app.api.utils.current_user import CurrentUser

import logging

from app.api.v1.services.send_mail import EmailService

logger = logging.getLogger(__name__)


class IncomingOrderService:
    @staticmethod
    def create_incoming_order(data, user_id, role):
        """Create a new incoming order.

        Args:
            data (dict): The incoming order data including supplier_id, product_id, and quantity_supply.
            user_id (int): The ID of the current user.
            role (str): The role of the current user ('admin' or 'supplier').

        Returns:
            dict: The created incoming order data.

        Raises:
            PermissionError: If the user doesn't have admin or supplier access.
            ValueError: If the supplier is not found or no stock exists for the product.
            Exception: For any other errors during the process.
        """
        if not CurrentUser.check_role(['admin', 'supplier']):
            logger.warning("Unauthorized attempt to create incoming order")
            raise PermissionError("Admin or supplier access required")

        try:
            # Validate the data
            schema = IncomingOrderSchema()
            validated_data = schema.load(data)
            logger.debug(f"Validated incoming order data: {validated_data}")

            # Set supply_date to current time
            validated_data['supply_date'] = datetime.utcnow()

            # Check if supplier is valid
            supplier = Supplier.get_by_id(validated_data['supplier_id'])
            if not supplier:
                logger.warning(f"Supplier ID {validated_data['supplier_id']} not found")
                raise ValueError("Supplier not found")

            # Check if user is authorized
            if role == 'supplier' and supplier.user_id != user_id:
                logger.warning(f"Supplier ID {validated_data['supplier_id']} access denied for user ID {user_id}")
                raise PermissionError("You can only create orders for yourself")

            # Check if stock exists
            stock = Stock.query.filter_by(product_id=validated_data['product_id']).first()
            if not stock:
                logger.warning(f"No stock found for product ID {validated_data['product_id']}")
                raise ValueError("No stock found for this product")

            # Calculate total price
            validated_data['total_price'] = validated_data['quantity_supply'] * stock.product_price

            # Create the order
            order = IncomingOrder(**validated_data)
            order.save()

            # Update stock
            stock.available_quantity += validated_data['quantity_supply']
            stock.total_price = stock.available_quantity * stock.product_price
            stock.save()

            # Update product
            product = Product.get_by_id(validated_data['product_id'])
            product.quantity = stock.available_quantity
            product.save()

            # Send email notification
            EmailService.send_incoming_order_created_email(supplier, product, order)

            logger.info(f"Incoming order created: ID {order.id} for product ID {order.product_id}")
            return schema.dump(order)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating incoming order: {str(e)}")
            raise

    @staticmethod
    def get_incoming_orders(user_id, role, page=1, per_page=10):
        """Retrieve all incoming orders with pagination.

        Args:
            user_id (int): The ID of the current user.
            role (str): The role of the current user ('admin' or 'supplier').
            page (int, optional): The page number for pagination. Defaults to 1.
            per_page (int, optional): The number of items per page. Defaults to 10.

        Returns:
            dict: A dictionary containing the incoming orders and pagination info.
                  Format: {"items": [...], "pagination": {...}}

        Raises:
            PermissionError: If the user doesn't have admin or supplier access.
            Exception: For any errors during the process.
        """
        if not CurrentUser.check_role(['admin', 'supplier']):
            logger.warning("Unauthorized attempt to access incoming orders")
            raise PermissionError("Admin or supplier access required")

        try:
            query = IncomingOrder.query

            # Filter by supplier if user is a supplier
            if role == 'supplier':
                supplier = Supplier.query.filter_by(user_id=user_id).first()
                if not supplier:
                    logger.warning(f"No supplier found for user ID {user_id}")
                    raise PermissionError("Supplier not found")
                query = query.filter_by(supplier_id=supplier.id)

            # Apply pagination
            orders_page = query.paginate(page=page, per_page=per_page, error_out=False)

            schema = IncomingOrderSchema(many=True)
            result = {
                "items": schema.dump(orders_page.items),
                "pagination": {
                    "page": orders_page.page,
                    "per_page": orders_page.per_page,
                    "total_pages": orders_page.pages,
                    "total_items": orders_page.total
                }
            }

            logger.info(
                f"Retrieved {len(orders_page.items)} incoming orders for role: {role} (page {page}/{orders_page.pages})")
            return result

        except Exception as e:
            logger.error(f"Error retrieving incoming orders: {str(e)}")
            raise

    @staticmethod
    def get_incoming_order_by_id(order_id, user_id, role):
        """Retrieve a specific incoming order by ID.

        Args:
            order_id (int): The ID of the incoming order to retrieve.
            user_id (int): The ID of the current user.
            role (str): The role of the current user ('admin' or 'supplier').

        Returns:
            dict: The incoming order data.

        Raises:
            PermissionError: If the user doesn't have admin or supplier access,
                             or if a supplier tries to access another supplier's order.
            ValueError: If the incoming order is not found.
            Exception: For any other errors during the process.
        """
        if not CurrentUser.check_role(['admin', 'supplier']):
            logger.warning(f"Unauthorized attempt to access incoming order ID: {order_id}")
            raise PermissionError("Admin or supplier access required")

        try:
            order = IncomingOrder.get_by_id(order_id)
            if not order:
                logger.warning(f"Incoming order ID {order_id} not found")
                raise ValueError("Incoming order not found")

            # Check if supplier is authorized to access this order
            if role == 'supplier':
                supplier = Supplier.query.filter_by(user_id=user_id).first()
                if not supplier or order.supplier_id != supplier.id:
                    logger.warning(f"Supplier access denied for incoming order ID {order_id}")
                    raise PermissionError("Access denied")

            schema = IncomingOrderSchema()
            logger.info(f"Incoming order retrieved: ID {order_id}")
            return schema.dump(order)

        except Exception as e:
            logger.error(f"Error retrieving incoming order ID {order_id}: {str(e)}")
            raise

    @staticmethod
    def update_incoming_order(order_id, data, user_id, role):
        """Update an existing incoming order.

        Args:
            order_id (int): The ID of the incoming order to update.
            data (dict): The updated incoming order data which may include quantity_supply.
            user_id (int): The ID of the current user.
            role (str): The role of the current user ('admin' or 'supplier').

        Returns:
            dict: The updated incoming order data.

        Raises:
            PermissionError: If the user doesn't have admin or supplier access,
                             or if a supplier tries to update another supplier's order.
            ValueError: If the incoming order is not found.
            Exception: For any other errors during the process.
        """
        if not CurrentUser.check_role(['admin', 'supplier']):
            logger.warning(f"Unauthorized attempt to update incoming order ID: {order_id}")
            raise PermissionError("Admin or supplier access required")

        try:
            # Get the existing order
            order = IncomingOrder.get_by_id(order_id)
            if not order:
                logger.warning(f"Incoming order ID {order_id} not found")
                raise ValueError("Incoming order not found")

            # Check if supplier is authorized to update this order
            if role == 'supplier':
                supplier = Supplier.query.filter_by(user_id=user_id).first()
                if not supplier or order.supplier_id != supplier.id:
                    logger.warning(f"Supplier access denied for updating incoming order ID {order_id}")
                    raise PermissionError("Access denied")

            # Validate the update data
            schema = IncomingOrderSchema(partial=True)
            validated_data = schema.load(data)

            # Get the previous quantity for stock adjustment
            old_quantity = order.quantity_supply

            # Update the order fields
            for key, value in validated_data.items():
                setattr(order, key, value)

            # If quantity is changed, update the stock and product
            if 'quantity_supply' in validated_data:
                stock = Stock.query.filter_by(product_id=order.product_id).first()

                # Adjust stock quantity (remove old quantity, add new quantity)
                quantity_difference = validated_data['quantity_supply'] - old_quantity
                stock.available_quantity += quantity_difference
                stock.total_price = stock.available_quantity * stock.product_price
                stock.save()

                # Update product quantity
                product = Product.get_by_id(order.product_id)
                product.quantity = stock.available_quantity
                product.save()

                # Update the total price of the order
                order.total_price = validated_data['quantity_supply'] * stock.product_price

            order.save()

            # Send email notification
            supplier = Supplier.get_by_id(order.supplier_id)
            product = Product.get_by_id(order.product_id)
            EmailService.send_incoming_order_updated_email(supplier, product, order)

            logger.info(f"Incoming order updated: ID {order.id}")
            return schema.dump(order)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating incoming order ID {order_id}: {str(e)}")
            raise

    @staticmethod
    def delete_incoming_order(order_id, role):
        """Delete an incoming order (admin only).

        Args:
            order_id (int): The ID of the incoming order to delete.
            role (str): The role of the current user.

        Returns:
            None

        Raises:
            PermissionError: If the user doesn't have admin access.
            ValueError: If the incoming order is not found.
            Exception: For any other errors during the process.
        """
        if role != 'admin':
            logger.warning(f"Non-admin user attempted to delete incoming order ID: {order_id}")
            raise PermissionError("Admin access required")

        try:
            # Get the existing order
            order = IncomingOrder.get_by_id(order_id)
            if not order:
                logger.warning(f"Incoming order ID {order_id} not found")
                raise ValueError("Incoming order not found")

            # Get the relevant data before deletion for stock adjustment
            product_id = order.product_id
            quantity = order.quantity_supply
            supplier_id = order.supplier_id

            # Delete the order
            order.delete()

            # Adjust stock
            stock = Stock.query.filter_by(product_id=product_id).first()
            if stock:
                stock.available_quantity -= quantity
                stock.total_price = stock.available_quantity * stock.product_price
                stock.save()

                # Update product quantity
                product = Product.get_by_id(product_id)
                product.quantity = stock.available_quantity
                product.save()

            # Send email notification
            supplier = Supplier.get_by_id(supplier_id)
            product = Product.get_by_id(product_id)
            EmailService.send_incoming_order_deleted_email(supplier, product, quantity)

            logger.info(f"Incoming order deleted: ID {order_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting incoming order ID {order_id}: {str(e)}")
            raise