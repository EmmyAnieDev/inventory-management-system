import logging

from app.api.db import db
from app.api.v1.models.stock import Stock
from app.api.v1.models.product import Product
from app.api.v1.schemas.stock import StockSchema

logger = logging.getLogger(__name__)


class StockService:
    """Service class for Stock-related business logic"""

    @staticmethod
    def get_all_stocks():
        """
        Retrieve all stock records

        Returns:
            list: Serialized list of all stock records
        """
        stocks = Stock.get_all()
        stock_schema = StockSchema(many=True)
        return stock_schema.dump(stocks)

    @staticmethod
    def get_stock_by_id(stock_id):
        """
        Retrieve a specific stock record by ID

        Args:
            stock_id (int): The ID of the stock record to retrieve

        Returns:
            dict: Serialized stock record or None if not found
        """
        stock = Stock.get_by_id(stock_id)
        if not stock:
            return None
        stock_schema = StockSchema()
        return stock_schema.dump(stock)

    @staticmethod
    def update_stock(stock_id, data):
        """
        Update a stock record and its associated product

        Args:
            stock_id (int): The ID of the stock to update
            data (dict): The data to update the stock with

        Returns:
            dict: Serialized updated stock record or None if not found
        """
        try:
            stock = Stock.get_by_id(stock_id)
            if not stock:
                return None

            # Update stock attributes from data
            for key, value in data.items():
                setattr(stock, key, value)

            # Calculate total price
            stock.total_price = stock.available_quantity * stock.product_price
            stock.save()

            # Update associated product
            StockService._update_associated_product(stock)

            stock_schema = StockSchema()
            return stock_schema.dump(stock)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating stock ID {stock_id}: {str(e)}")
            raise

    @staticmethod
    def _update_associated_product(stock):
        """
        Update the associated product with stock values

        Args:
            stock (Stock): The stock object with updated values
        """
        try:
            product = Product.get_by_id(stock.product_id)
            if product:
                product.quantity = stock.available_quantity
                product.price = stock.product_price
                product.save()
        except Exception as e:
            logger.error(f"Error updating associated product for stock ID {stock.id}: {str(e)}")
            raise