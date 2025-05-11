from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from marshmallow import ValidationError
import logging

from app.api.utils.current_user import CurrentUser
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.v1.services.category import CategoryService

logger = logging.getLogger(__name__)

bp = Blueprint("category", __name__, url_prefix="/categories")

@bp.route("/", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Category'],
    'description': 'Create a new category (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'Electronics'}
            },
            'required': ['name']
        }}
    ],
    'responses': {
        201: {'description': 'Category created successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input','schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Admin access required','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def create_category():
    """Create a new category"""
    if not CurrentUser.check_role(['admin']):
        logger.warning("Unauthorized attempt to create category")
        return error_response(403, "Admin access required")

    try:
        data = request.get_json()
        category_data, status_code, message = CategoryService.create_category(data)
        return success_response(status_code, message, category_data)
    except ValidationError as e:
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Category'],
    'description': 'Retrieve all categories (accessible to all authenticated users).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Categories retrieved successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_categories():
    """Get All Categories"""
    if not CurrentUser.check_role(['admin', 'customer', 'supplier']):
        logger.warning("Unauthorized attempt to access categories")
        return error_response(403, "Access denied")

    try:
        categories_data, status_code, message = CategoryService.get_all_categories()
        return success_response(status_code, message, categories_data)
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Category'],
    'description': 'Retrieve a specific category by ID (accessible to all authenticated users).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Category retrieved successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Category not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_category(id):
    """Get Single Category"""
    if not CurrentUser.check_role(['admin', 'customer', 'supplier']):
        logger.warning(f"Unauthorized attempt to access category ID: {id}")
        return error_response(403, "Access denied")

    try:
        category_data, status_code, message = CategoryService.get_category_by_id(id)
        if status_code == 404:
            return error_response(status_code, message)
        return success_response(status_code, message, category_data)
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Category'],
    'description': 'Update a category by ID (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'Updated Electronics'}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Category updated successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input','schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Admin access required','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Category not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_category(id):
    """Update Category"""
    if not CurrentUser.check_role(['admin']):
        logger.warning(f"Unauthorized attempt to update category ID: {id}")
        return error_response(403, "Admin access required")

    try:
        data = request.get_json()
        category_data, status_code, message = CategoryService.update_category(id, data)
        if status_code in [400, 404]:
            return error_response(status_code, message)
        return success_response(status_code, message, category_data)
    except ValidationError as e:
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Category'],
    'description': 'Delete a category by ID (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Category deleted successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Admin access required','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Category not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def delete_category(id):
    """Delete Category"""
    if not CurrentUser.check_role(['admin']):
        logger.warning(f"Unauthorized attempt to delete category ID: {id}")
        return error_response(403, "Admin access required")

    try:
        result, status_code, message = CategoryService.delete_category(id)
        if status_code in [400, 404]:
            return error_response(status_code, message)
        return success_response(status_code, message, result)
    except Exception as e:
        return error_response(500, "An unexpected error occurred")