import logging
from marshmallow import ValidationError

from app.api.db import db
from app.api.v1.models.category import Category
from app.api.v1.schemas.category import CategorySchema

logger = logging.getLogger(__name__)


class CategoryService:
    """Service class to handle business logic for category operations"""

    @staticmethod
    def create_category(data):
        """
        Create a new category

        Args:
            data (dict): Category data to validate and save

        Returns:
            tuple: (category_dict, status_code, message)

        Raises:
            ValidationError: If input data is invalid
            Exception: For unexpected errors
        """
        try:
            schema = CategorySchema()
            validated_data = schema.load(data)
            logger.debug(f"Validated category data: {validated_data}")

            category = Category(**validated_data)
            category.save()
            logger.info(f"Category created: {category.name} (ID: {category.id})")

            return schema.dump(category), 201, "Category created successfully"
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Unexpected error creating category: {str(e)}")
            raise

    @staticmethod
    def get_all_categories():
        """
        Get all categories

        Returns:
            tuple: (categories_list, status_code, message)

        Raises:
            Exception: For unexpected errors
        """
        try:
            categories = Category.get_all()
            schema = CategorySchema(many=True)
            logger.info(f"Retrieved {len(categories)} categories")
            return schema.dump(categories), 200, "Categories retrieved successfully"
        except Exception as e:
            logger.critical(f"Unexpected error retrieving categories: {str(e)}")
            raise

    @staticmethod
    def get_category_by_id(category_id):
        """
        Get a single category by ID

        Args:
            category_id (int): ID of the category to retrieve

        Returns:
            tuple: (category_dict, status_code, message)

        Raises:
            Exception: For unexpected errors
        """
        try:
            category = Category.get_by_id(category_id)
            if not category:
                logger.warning(f"Category ID {category_id} not found")
                return None, 404, "Category not found"

            schema = CategorySchema()
            logger.info(f"Category retrieved: {category.name} (ID: {category_id})")
            return schema.dump(category), 200, "Category retrieved successfully"
        except Exception as e:
            logger.critical(f"Unexpected error retrieving category ID {category_id}: {str(e)}")
            raise

    @staticmethod
    def update_category(category_id, data):
        """
        Update a category by ID

        Args:
            category_id (int): ID of the category to update
            data (dict): Updated category data

        Returns:
            tuple: (category_dict, status_code, message)

        Raises:
            ValidationError: If input data is invalid
            Exception: For unexpected errors
        """
        try:
            category = Category.get_by_id(category_id)
            if not category:
                logger.warning(f"Category ID {category_id} not found")
                return None, 404, "Category not found"

            schema = CategorySchema(partial=True)
            validated_data = schema.load(data)
            logger.debug(f"Validated update data for category ID {category_id}: {validated_data}")

            for key, value in validated_data.items():
                setattr(category, key, value)

            category.save()
            logger.info(f"Category updated: {category.name} (ID: {category_id})")
            return schema.dump(category), 200, "Category updated successfully"
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Unexpected error updating category ID {category_id}: {str(e)}")
            raise

    @staticmethod
    def delete_category(category_id):
        """
        Delete a category by ID

        Args:
            category_id (int): ID of the category to delete

        Returns:
            tuple: (empty_dict, status_code, message)

        Raises:
            Exception: For unexpected errors
        """
        try:
            category = Category.get_by_id(category_id)
            if not category:
                logger.warning(f"Category ID {category_id} not found")
                return None, 404, "Category not found"

            if category.products:
                logger.warning(f"Cannot delete category ID {category_id} with associated products")
                return None, 400, "Cannot delete category with associated products"

            category.delete()
            logger.info(f"Category deleted: ID {category_id}")
            return {}, 200, "Category deleted successfully"
        except Exception as e:
            db.session.rollback()
            logger.critical(f"Unexpected error deleting category ID {category_id}: {str(e)}")
            raise