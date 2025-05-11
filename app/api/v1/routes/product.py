from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from marshmallow import ValidationError
import logging

from app.api.utils.current_user import CurrentUser
from app.api.v1.services.product import ProductService
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response

logger = logging.getLogger(__name__)

bp = Blueprint("product", __name__, url_prefix="/products")

@bp.route("/", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Product'],
    'description': 'Create a new product and initialize stock (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'Laptop'},
                'category_id': {'type': 'integer', 'example': 1},
                'quantity': {'type': 'integer', 'example': 100},
                'price': {'type': 'number', 'example': 999.99}
            },
            'required': ['name', 'category_id', 'quantity', 'price']
        }}
    ],
    'responses': {
        201: {'description': 'Product created successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input','schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Admin access required','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def create_product():
    """Create Product"""
    if not CurrentUser.check_role(['admin']):
        logger.warning("Unauthorized attempt to create product")
        return error_response(403, "Admin access required")

    try:
        data = request.get_json()
        product_data, status_code, message = ProductService.create_product(data)
        return success_response(status_code, message, product_data)
    except ValidationError as e:
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Product'],
    'description': 'Retrieve all products (accessible to all authenticated users).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Products retrieved successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_products():
    """Get all products"""
    if not CurrentUser.check_role(['admin', 'customer', 'supplier']):
        logger.warning("Unauthorized attempt to access products")
        return error_response(403, "Access denied")

    try:
        products_data, status_code, message = ProductService.get_all_products()
        return success_response(status_code, message, products_data)
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Product'],
    'description': 'Retrieve a specific product by ID (accessible to all authenticated users).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Product retrieved successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Product not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_product(id):
    """Get Single Product"""
    if not CurrentUser.check_role(['admin', 'customer', 'supplier']):
        logger.warning(f"Unauthorized attempt to access product ID: {id}")
        return error_response(403, "Access denied")

    try:
        product_data, status_code, message = ProductService.get_product_by_id(id)
        if status_code == 404:
            return error_response(status_code, message)
        return success_response(status_code, message, product_data)
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Product'],
    'description': 'Update a product by ID (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'Updated Laptop'},
                'category_id': {'type': 'integer', 'example': 1},
                'quantity': {'type': 'integer', 'example': 150},
                'price': {'type': 'number', 'example': 1099.99}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Product updated successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input','schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Admin access required','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Product not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_product(id):
    """Update Product"""
    if not CurrentUser.check_role(['admin']):
        logger.warning(f"Unauthorized attempt to update product ID: {id}")
        return error_response(403, "Admin access required")

    try:
        data = request.get_json()
        product_data, status_code, message = ProductService.update_product(id, data)
        if status_code == 404:
            return error_response(status_code, message)
        return success_response(status_code, message, product_data)
    except ValidationError as e:
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Product'],
    'description': 'Delete a product by ID (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Product deleted successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Admin access required','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Product not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def delete_product(id):
    """Delete Product"""
    if not CurrentUser.check_role(['admin']):
        logger.warning(f"Unauthorized attempt to delete product ID: {id}")
        return error_response(403, "Admin access required")

    try:
        result, status_code, message = ProductService.delete_product(id)
        if status_code == 404:
            return error_response(status_code, message)
        return success_response(status_code, message, result)
    except Exception as e:
        return error_response(500, "An unexpected error occurred")