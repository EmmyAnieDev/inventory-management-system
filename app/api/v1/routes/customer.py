from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.api.v1.services.customer import CustomerService
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.utils.current_user import CurrentUser
from flasgger import swag_from
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

bp = Blueprint("customer", __name__, url_prefix="/customers")

@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Customer'],
    'description': 'Get all customer profiles (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 10}
    ],
    'responses': {
        200: {'description': 'Customers retrieved successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_all_customers():
    """Get All Customers (Admin only)"""
    try:
        role = CurrentUser.get_role()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result = CustomerService.get_all_customers(page, per_page, role)
        return success_response(200, "Customers retrieved successfully", result)

    except PermissionError as e:
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving customers: {str(e)}")
        return error_response(500, "An unexpected error occurred")

@bp.route("/<int:customer_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Customer'],
    'description': 'Retrieve a customer profile by customer ID (primary key).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'customer_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Customer retrieved successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Customer not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_customer(customer_id):
    """Get Customer Profile by Customer ID"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        result = CustomerService.get_customer(customer_id, user_id, role)
        return success_response(200, "Customer retrieved successfully", result)

    except ValueError as e:
        return error_response(404, str(e))
    except PermissionError as e:
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving customer ID {customer_id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")

@bp.route("/<int:customer_id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Customer'],
    'description': 'Update a customer profile by customer ID.',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'customer_id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'first_name': {'type': 'string', 'example': 'John'},
                'last_name': {'type': 'string', 'example': 'Doe'},
                'age': {'type': 'integer', 'example': 30},
                'email': {'type': 'string', 'example': 'john.doe@example.com'},
                'phone_number': {'type': 'string', 'example': '1234567890'},
                'address': {'type': 'string', 'example': '123 Main St'}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Customer updated successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input','schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Customer not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_customer(customer_id):
    """Update Customer Profile"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        data = request.get_json()

        result = CustomerService.update_customer(customer_id, user_id, role, data)
        return success_response(200, "Customer updated successfully", result)

    except ValueError as e:
        return error_response(404, str(e))
    except PermissionError as e:
        return error_response(403, str(e))
    except ValidationError as e:
        return error_response(400, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error updating customer ID {customer_id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")

@bp.route("/<int:customer_id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Customer'],
    'description': 'Delete a customer profile by customer ID (self or admin access).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'customer_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Customer deleted successfully','schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied','schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Customer not found','schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error','schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def delete_customer(customer_id):
    """Delete Customer"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        CustomerService.delete_customer(customer_id, user_id, role)
        return success_response(200, "Customer deleted successfully", {})

    except ValueError as e:
        return error_response(404, str(e))
    except PermissionError as e:
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error deleting customer ID {customer_id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")