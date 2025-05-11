import logging
from marshmallow import ValidationError

from app.api.db import db
from app.api.v1.models.product import Product
from app.api.v1.models.stock import Stock
from app.api.v1.schemas.product import ProductSchema

logger = logging.getLogger(__name__)


class ProductService:
    """Service class to handle business logic for product operations"""

    @staticmethod
    def create_product(data):
        """
        Create a new product and initialize stock

        Args:
            data (dict): Product data to validate and save

        Returns:
            tuple: (product_dict, status_code, message)

        Raises:
            ValidationError: If input data is invalid
            Exception: For unexpected errors
        """
        try:
            schema = ProductSchema()
            validated_data = schema.load(data)
            logger.debug(f"Validated product data: {validated_data}")

            product = Product(**validated_data)
            product.save()

            # Initialize stock
            stock = Stock(
                product_id=product.id,
                available_quantity=product.quantity,
                product_price=product.price,
                total_price=product.quantity * product.price
            )
            stock.save()
            logger.info(f"Product created: {product.name} (ID: {product.id}) with stock")

            return schema.dump(product), 201, "Product created successfully"
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Unexpected error creating product: {str(e)}")
            raise

    @staticmethod
    def get_all_products():
        """
        Get all products

        Returns:
            tuple: (products_list, status_code, message)

        Raises:
            Exception: For unexpected errors
        """
        try:
            products = Product.get_all()
            schema = ProductSchema(many=True)
            logger.info(f"Retrieved {len(products)} products")
            return schema.dump(products), 200, "Products retrieved successfully"
        except Exception as e:
            logger.critical(f"Unexpected error retrieving products: {str(e)}")
            raise

    @staticmethod
    def get_product_by_id(product_id):
        """
        Get a single product by ID

        Args:
            product_id (int): ID of the product to retrieve

        Returns:
            tuple: (product_dict, status_code, message)

        Raises:
            Exception: For unexpected errors
        """
        try:
            product = Product.get_by_id(product_id)
            if not product:
                logger.warning(f"Product ID {product_id} not found")
                return None, 404, "Product not found"

            schema = ProductSchema()
            logger.info(f"Product retrieved: {product.name} (ID: {product_id})")
            return schema.dump(product), 200, "Product retrieved successfully"
        except Exception as e:
            logger.critical(f"Unexpected error retrieving product ID {product_id}: {str(e)}")
            raise

    @staticmethod
    def update_product(product_id, data):
        """
        Update a product by ID

        Args:
            product_id (int): ID of the product to update
            data (dict): Updated product data

        Returns:
            tuple: (product_dict, status_code, message)

        Raises:
            ValidationError: If input data is invalid
            Exception: For unexpected errors
        """
        try:
            product = Product.get_by_id(product_id)
            if not product:
                logger.warning(f"Product ID {product_id} not found")
                return None, 404, "Product not found"

            schema = ProductSchema(partial=True)
            validated_data = schema.load(data)
            logger.debug(f"Validated update data for product ID {product_id}: {validated_data}")

            for key, value in validated_data.items():
                setattr(product, key, value)

            product.save()

            # Update stock
            stock = Stock.query.filter_by(product_id=product.id).first()
            if stock:
                stock.available_quantity = product.quantity
                stock.product_price = product.price
                stock.total_price = product.quantity * product.price
                stock.save()

            logger.info(f"Product updated: {product.name} (ID: {product_id})")
            return schema.dump(product), 200, "Product updated successfully"
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Unexpected error updating product ID {product_id}: {str(e)}")
            raise

    @staticmethod
    def delete_product(product_id):
        """
        Delete a product by ID

        Args:
            product_id (int): ID of the product to delete

        Returns:
            tuple: (empty_dict, status_code, message)

        Raises:
            Exception: For unexpected errors
        """
        try:
            product = Product.get_by_id(product_id)
            if not product:
                logger.warning(f"Product ID {product_id} not found")
                return None, 404, "Product not found"

            stock = Stock.query.filter_by(product_id=product.id).first()
            if stock:
                stock.delete()

            product.delete()
            logger.info(f"Product deleted: ID {product_id}")
            return {}, 200, "Product deleted successfully"
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Unexpected error deleting product ID {product_id}: {str(e)}")
            raise