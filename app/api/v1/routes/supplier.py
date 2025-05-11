from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.utils.current_user import CurrentUser
from flasgger import swag_from
from marshmallow import ValidationError
import logging

from app.api.v1.services.supplier import SupplierService

logger = logging.getLogger(__name__)

bp = Blueprint("supplier", __name__, url_prefix="/suppliers")

@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Supplier'],
    'description': 'Get all supplier profiles (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 10}
    ],
    'responses': {
        200: {'description': 'Suppliers retrieved successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_all_suppliers():
    """Get All Suppliers (Admin only)"""
    try:
        role = CurrentUser.get_role()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result = SupplierService.get_all_suppliers(page, per_page, role)
        return success_response(200, "Suppliers retrieved successfully", result)

    except PermissionError as e:
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving suppliers: {str(e)}")
        return error_response(500, "An unexpected error occurred")

@bp.route("/<int:supplier_id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Supplier'],
    'description': 'Retrieve a supplier profile by supplier ID (primary key).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'supplier_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Supplier retrieved successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Supplier not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_supplier(supplier_id):
    """Get Supplier Profile by Supplier ID"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        result = SupplierService.get_supplier(supplier_id, user_id, role)
        return success_response(200, "Supplier retrieved successfully", result)

    except ValueError as e:
        return error_response(404, str(e))
    except PermissionError as e:
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving supplier ID {supplier_id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")

@bp.route("/<int:supplier_id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Supplier'],
    'description': 'Update a supplier profile by supplier ID.',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'supplier_id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'first_name': {'type': 'string', 'example': 'Jane'},
                'last_name': {'type': 'string', 'example': 'Smith'},
                'age': {'type': 'integer', 'example': 40},
                'email': {'type': 'string', 'example': 'jane.smith@example.com'},
                'phone_number': {'type': 'string', 'example': '0987654321'},
                'address': {'type': 'string', 'example': '456 Oak St'}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Supplier updated successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Supplier not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_supplier(supplier_id):
    """Update Supplier Profile"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        data = request.get_json()

        result = SupplierService.update_supplier(supplier_id, user_id, role, data)
        return success_response(200, "Supplier updated successfully", result)

    except ValueError as e:
        return error_response(404, str(e))
    except PermissionError as e:
        return error_response(403, str(e))
    except ValidationError as e:
        return error_response(400, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error updating supplier ID {supplier_id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")

@bp.route("/<int:supplier_id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Supplier'],
    'description': 'Delete a supplier profile by supplier ID (self or admin access).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'supplier_id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Supplier deleted successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Supplier not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def delete_supplier(supplier_id):
    """Delete Supplier"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        SupplierService.delete_supplier(supplier_id, user_id, role)
        return success_response(200, "Supplier deleted successfully", {})

    except ValueError as e:
        return error_response(404, str(e))
    except PermissionError as e:
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error deleting supplier ID {supplier_id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")