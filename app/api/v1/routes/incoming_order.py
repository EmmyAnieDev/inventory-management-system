from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from marshmallow import ValidationError
import logging

from app.api.v1.services.incoming_order import IncomingOrderService
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.utils.current_user import CurrentUser

logger = logging.getLogger(__name__)

bp = Blueprint("incoming-order", __name__, url_prefix="/incoming-orders")

@bp.route("/", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Incoming Order'],
    'description': 'Create a new incoming order (admin or supplier).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer', 'example': 1},
                'supplier_id': {'type': 'integer', 'example': 1},
                'quantity_supply': {'type': 'integer', 'example': 50}
            },
            'required': ['product_id', 'supplier_id', 'quantity_supply']
        }}
    ],
    'responses': {
        201: {
            'description': 'Incoming order created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'status': {'type': 'string', 'example': 'success'},
                    'message': {'type': 'string', 'example': 'Incoming order created successfully'},
                    'data': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer', 'example': 1},
                            'product_id': {'type': 'integer', 'example': 1},
                            'supplier_id': {'type': 'integer', 'example': 1},
                            'quantity_supply': {'type': 'integer', 'example': 50},
                            'total_price': {'type': 'number', 'example': 500.0},
                            'supply_date': {'type': 'string', 'format': 'date-time', 'example': '2025-05-11T12:00:00Z'},
                            'date_created': {'type': 'string', 'format': 'date-time', 'example': '2025-05-11T12:00:00Z'}
                        }
                    }
                }
            }
        },
        400: {'description': 'Invalid input', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def create_incoming_order():
    """Create Incoming Order"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        data = request.get_json()

        result = IncomingOrderService.create_incoming_order(data, user_id, role)
        return success_response(201, "Incoming order created successfully", result)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(400, f"Invalid input: {str(e)}")
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except ValueError as e:
        logger.warning(f"Value error: {str(e)}")
        return error_response(400, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error creating incoming order: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Incoming Order'],
    'description': 'Retrieve all incoming orders (admin sees all, suppliers see own).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 10}
    ],
    'responses': {
        200: {'description': 'Incoming orders retrieved successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_incoming_orders():
    """Get All Incoming Orders"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result = IncomingOrderService.get_incoming_orders(user_id, role, page, per_page)
        return success_response(200, "Incoming orders retrieved successfully", result)
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving incoming orders: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Incoming Order'],
    'description': 'Retrieve a specific incoming order by ID (admin or supplier who owns it).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Incoming order retrieved successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Incoming order not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_incoming_order(id):
    """Get Single Incoming Order"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        result = IncomingOrderService.get_incoming_order_by_id(id, user_id, role)
        return success_response(200, "Incoming order retrieved successfully", result)
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except ValueError as e:
        logger.warning(f"Value error: {str(e)}")
        return error_response(404, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving incoming order ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Incoming Order'],
    'description': 'Update an existing incoming order (admin or supplier who owns it).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'quantity_supply': {'type': 'integer', 'example': 50},
            }
        }}
    ],
    'responses': {
        200: {'description': 'Incoming order updated successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Incoming order not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_incoming_order(id):
    """Update Incoming Order"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        data = request.get_json()

        result = IncomingOrderService.update_incoming_order(id, data, user_id, role)
        return success_response(200, "Incoming order updated successfully", result)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(400, f"Invalid input: {str(e)}")
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except ValueError as e:
        logger.warning(f"Value error: {str(e)}")
        return error_response(404, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error updating incoming order ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Incoming Order'],
    'description': 'Delete an incoming order (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Incoming order deleted successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Incoming order not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def delete_incoming_order(id):
    """Delete Incoming Order"""
    try:
        role = CurrentUser.get_role()

        IncomingOrderService.delete_incoming_order(id, role)
        return success_response(200, "Incoming order deleted successfully", {})
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except ValueError as e:
        logger.warning(f"Value error: {str(e)}")
        return error_response(404, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error deleting incoming order ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")