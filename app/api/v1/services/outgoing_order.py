from datetime import datetime

from app.api.db import db
from app.api.v1.models.customer import Customer
from app.api.v1.models.product import Product
from app.api.v1.models.stock import Stock
from app.api.v1.models.outgoing_order import OutgoingOrder
from app.api.v1.models.user import User
from app.api.v1.schemas.outgoing_order import OutgoingOrderSchema
from app.api.utils.current_user import CurrentUser
from flask_mail import Message
from app import mail
import logging

from app.api.v1.services.send_mail import EmailService
from config import config

logger = logging.getLogger(__name__)


class OutgoingOrderService:

    @staticmethod
    def create_outgoing_order(data, user_id, role):
        """
        Create a new outgoing order.

        Args:
            data (dict): The order data including product_id, customer_id, quantity_order, etc.
            user_id (int): The ID of the current authenticated user
            role (str): The role of the current authenticated user

        Returns:
            dict: The created outgoing order data

        Raises:
            PermissionError: If the user does not have the required role
            ValueError: If input data is invalid or stock is insufficient
            ValidationError: If the schema validation fails
            Exception: For any other unexpected errors
        """
        if not CurrentUser.check_role(['admin', 'customer']):
            logger.warning("Unauthorized attempt to create outgoing order")
            raise PermissionError("Admin or customer access required")

        try:
            # Validate the data
            schema = OutgoingOrderSchema()
            validated_data = schema.load(data)
            logger.debug(f"Validated outgoing order data: {validated_data}")

            # Set order_date to current time
            validated_data['order_date'] = datetime.utcnow()

            # Check if customer is valid and authorized
            customer = Customer.get_by_id(validated_data['customer_id'])
            if not customer:
                logger.warning(f"Customer ID {validated_data['customer_id']} not found")
                raise ValueError("Customer not found")

            if role == 'customer' and customer.user_id != user_id:
                logger.warning(f"Customer ID {validated_data['customer_id']} access denied for user ID {user_id}")
                raise PermissionError("You can only create orders for yourself")

            # Check if stock exists and is sufficient
            stock = Stock.query.filter_by(product_id=validated_data['product_id']).first()
            if not stock:
                logger.warning(f"No stock found for product ID {validated_data['product_id']}")
                raise ValueError("No stock found for this product")

            if stock.available_quantity < validated_data['quantity_order']:
                logger.warning(f"Insufficient stock for product ID {validated_data['product_id']}")
                raise ValueError("Insufficient stock available")

            # Calculate prices
            validated_data['total_price'] = validated_data['quantity_order'] * stock.product_price

            # Apply discount if available
            if 'discount' in validated_data and validated_data['discount']:
                discount_factor = 1 - (validated_data['discount'] / 100)
                validated_data['total_price_to_pay'] = validated_data['total_price'] * discount_factor
            else:
                validated_data['discount'] = 0
                validated_data['total_price_to_pay'] = validated_data['total_price']

            # Create the order
            order = OutgoingOrder(**validated_data)
            order.save()

            # Update stock
            stock.available_quantity -= validated_data['quantity_order']
            stock.total_price = stock.available_quantity * stock.product_price
            stock.save()

            # Update product
            product = Product.get_by_id(validated_data['product_id'])
            product.quantity = stock.available_quantity
            product.save()

            # Send email notification to customer
            EmailService.send_outgoing_order_created_email(customer, product, order)

            # Check for low stock and notify admin
            OutgoingOrderService._check_low_stock(stock, product)

            logger.info(f"Outgoing order created: ID {order.id} for product ID {order.product_id}")
            return schema.dump(order)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating outgoing order: {str(e)}")
            raise


    @staticmethod
    def get_outgoing_orders(user_id, role, page=1, per_page=10):
        """
        Retrieve all outgoing orders with pagination.

        Args:
            user_id (int): The ID of the current authenticated user
            role (str): The role of the current authenticated user
            page (int, optional): The page number to retrieve. Defaults to 1.
            per_page (int, optional): The number of records per page. Defaults to 10.

        Returns:
            dict: Dictionary containing order items and pagination information

        Raises:
            PermissionError: If the user does not have the required role
            Exception: For any other unexpected errors
        """
        if not CurrentUser.check_role(['admin', 'customer']):
            logger.warning("Unauthorized attempt to access outgoing orders")
            raise PermissionError("Admin or customer access required")

        try:
            query = OutgoingOrder.query

            # Filter by customer if user is a customer
            if role == 'customer':
                customer = Customer.query.filter_by(user_id=user_id).first()
                if not customer:
                    logger.warning(f"No customer found for user ID {user_id}")
                    raise PermissionError("Customer not found")
                query = query.filter_by(customer_id=customer.id)

            # Apply pagination
            orders_page = query.paginate(page=page, per_page=per_page, error_out=False)

            schema = OutgoingOrderSchema(many=True)
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
                f"Retrieved {len(orders_page.items)} outgoing orders for role: {role} (page {page}/{orders_page.pages})")
            return result

        except Exception as e:
            logger.error(f"Error retrieving outgoing orders: {str(e)}")
            raise


    @staticmethod
    def get_outgoing_order_by_id(order_id, user_id, role):
        """
        Retrieve a specific outgoing order by ID.

        Args:
            order_id (int): The ID of the order to retrieve
            user_id (int): The ID of the current authenticated user
            role (str): The role of the current authenticated user

        Returns:
            dict: The outgoing order data

        Raises:
            PermissionError: If the user does not have the required role or access
            ValueError: If the order is not found
            Exception: For any other unexpected errors
        """
        if not CurrentUser.check_role(['admin', 'customer']):
            logger.warning(f"Unauthorized attempt to access outgoing order ID: {order_id}")
            raise PermissionError("Admin or customer access required")

        try:
            order = OutgoingOrder.get_by_id(order_id)
            if not order:
                logger.warning(f"Outgoing order ID {order_id} not found")
                raise ValueError("Outgoing order not found")

            # Check if customer is authorized to access this order
            if role == 'customer':
                customer = Customer.query.filter_by(user_id=user_id).first()
                if not customer or order.customer_id != customer.id:
                    logger.warning(f"Customer access denied for outgoing order ID {order_id}")
                    raise PermissionError("Access denied")

            schema = OutgoingOrderSchema()
            logger.info(f"Outgoing order retrieved: ID {order_id}")
            return schema.dump(order)

        except Exception as e:
            logger.error(f"Error retrieving outgoing order ID {order_id}: {str(e)}")
            raise


    @staticmethod
    def update_outgoing_order(order_id, data, role):
        """
        Update an existing outgoing order (admin only).

        Args:
            order_id (int): The ID of the order to update
            data (dict): The updated order data
            role (str): The role of the current authenticated user

        Returns:
            dict: The updated outgoing order data

        Raises:
            PermissionError: If the user does not have the required role
            ValueError: If the order is not found or stock is insufficient
            ValidationError: If the schema validation fails
            Exception: For any other unexpected errors
        """
        # Only admin can update orders
        if role != 'admin':
            logger.warning(f"Non-admin user attempted to update outgoing order ID: {order_id}")
            raise PermissionError("Admin access required")

        try:
            # Get the existing order
            order = OutgoingOrder.get_by_id(order_id)
            if not order:
                logger.warning(f"Outgoing order ID {order_id} not found")
                raise ValueError("Outgoing order not found")

            # Validate the update data
            schema = OutgoingOrderSchema(partial=True)
            validated_data = schema.load(data)

            # Get the previous quantity for stock adjustment
            old_quantity = order.quantity_order

            # Get the product
            product = Product.get_by_id(order.product_id)
            if not product:
                logger.warning(f"Product not found for order ID {order.id}")
                raise ValueError("Product not found for this order")

            # Check if quantity is being updated and if stock is sufficient
            if 'quantity_order' in validated_data:
                stock = Stock.query.filter_by(product_id=order.product_id).first()

                # Calculate how much more stock is needed
                quantity_difference = validated_data['quantity_order'] - old_quantity

                # Check if the additional quantity is available in stock
                if quantity_difference > 0 and stock.available_quantity < quantity_difference:
                    logger.warning(f"Insufficient stock for update to product ID {order.product_id}")
                    raise ValueError("Insufficient stock available for this update")

                # Update the stock
                stock.available_quantity -= quantity_difference
                stock.total_price = stock.available_quantity * stock.product_price
                stock.save()

                # Update product quantity
                product.quantity = stock.available_quantity
                product.save()

                # Update the total price of the order
                validated_data['total_price'] = validated_data['quantity_order'] * stock.product_price

                # Update total price to pay if discount is present
                if 'discount' in validated_data:
                    discount_factor = 1 - (validated_data['discount'] / 100)
                else:
                    discount_factor = 1 - (order.discount / 100)

                validated_data['total_price_to_pay'] = validated_data['total_price'] * discount_factor

                # Check for low stock after update
                OutgoingOrderService._check_low_stock(stock, product)
            elif 'discount' in validated_data:
                # If only discount changed, recalculate total_price_to_pay
                discount_factor = 1 - (validated_data['discount'] / 100)
                validated_data['total_price_to_pay'] = order.total_price * discount_factor

            # Update the order fields
            for key, value in validated_data.items():
                setattr(order, key, value)

            order.save()

            # Retrieve the customer associated with this order
            customer = Customer.get_by_id(order.customer_id)
            if not customer:
                logger.warning(f"Customer not found for order ID {order.id}")
                raise ValueError("Customer not found for this order")

            # Send email notification to customer
            EmailService.send_outgoing_order_updated_email(customer, product, order)

            logger.info(f"Outgoing order updated: ID {order.id}")
            return schema.dump(order)

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating outgoing order ID {order_id}: {str(e)}")
            raise


    @staticmethod
    def delete_outgoing_order(order_id, role):
        """
        Delete an outgoing order (admin only).

        Args:
            order_id (int): The ID of the order to delete
            role (str): The role of the current authenticated user

        Raises:
            PermissionError: If the user does not have the required role
            ValueError: If the order is not found
            Exception: For any other unexpected errors
        """
        # Only admin can delete orders
        if role != 'admin':
            logger.warning(f"Non-admin user attempted to delete outgoing order ID: {order_id}")
            raise PermissionError("Admin access required")

        try:
            # Get the existing order
            order = OutgoingOrder.get_by_id(order_id)
            if not order:
                logger.warning(f"Outgoing order ID {order_id} not found")
                raise ValueError("Outgoing order not found")

            # Get the relevant data before deletion for stock adjustment
            product_id = order.product_id
            quantity = order.quantity_order
            customer_id = order.customer_id

            # Delete the order
            order.delete()

            # Return the quantities back to stock
            stock = Stock.query.filter_by(product_id=product_id).first()
            if stock:
                stock.available_quantity += quantity
                stock.total_price = stock.available_quantity * stock.product_price
                stock.save()

                # Update product quantity
                product = Product.get_by_id(product_id)
                product.quantity = stock.available_quantity
                product.save()

            # Send email notification to customer
            customer = Customer.get_by_id(customer_id)
            product = Product.get_by_id(product_id)
            EmailService.send_outgoing_order_deleted_email(customer, product, order)

            logger.info(f"Outgoing order deleted: ID {order_id}")

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting outgoing order ID {order_id}: {str(e)}")
            raise

    @staticmethod
    def _check_low_stock(stock, product):
        """
        Check if stock is low and notify admin if necessary.

        Args:
            stock (Stock): The stock object to check
            product (Product): The product related to the stock

        Returns:
            None
        """
        try:
            if stock.available_quantity < config.LOW_STOCK_THRESHOLD:
                admin = User.query.filter_by(role='admin').first()
                if admin:

                    # Send email notification to admin
                    EmailService.send_low_stock_alert_email(admin, product, stock)

                    logger.info(f"Low stock alert sent for product ID {product.id}")
        except Exception as e:
            logger.error(f"Error sending low stock alert: {str(e)}")