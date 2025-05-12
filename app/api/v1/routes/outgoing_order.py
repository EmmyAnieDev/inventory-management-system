from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from marshmallow import ValidationError
import logging

from app.api.v1.services.outgoing_order import OutgoingOrderService
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.utils.current_user import CurrentUser

logger = logging.getLogger(__name__)

bp = Blueprint("outgoing-order", __name__, url_prefix="/outgoing-orders")


@bp.route("/", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Outgoing Order'],
    'description': 'Create a new outgoing order (admin or customer).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'product_id': {'type': 'integer', 'example': 1},
                'customer_id': {'type': 'integer', 'example': 1},
                'quantity_order': {'type': 'integer', 'example': 10},
                'discount': {'type': 'number', 'example': 10.0},
            },
            'required': ['product_id', 'customer_id', 'quantity_order']
        }}
    ],
    'responses': {
        201: {'description': 'Outgoing order created successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input or insufficient stock', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def create_outgoing_order():
    """Create Outgoing Order"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        data = request.get_json()

        result = OutgoingOrderService.create_outgoing_order(data, user_id, role)
        return success_response(201, "Outgoing order created successfully", result)
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
        logger.critical(f"Unexpected error creating outgoing order: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Outgoing Order'],
    'description': 'Retrieve all outgoing orders (admin sees all, customers see own).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 1},
        {'name': 'per_page', 'in': 'query', 'type': 'integer', 'required': False, 'default': 10}
    ],
    'responses': {
        200: {'description': 'Outgoing orders retrieved successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_outgoing_orders():
    """Get All Outgoing Orders"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        result = OutgoingOrderService.get_outgoing_orders(user_id, role, page, per_page)
        return success_response(200, "Outgoing orders retrieved successfully", result)
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving outgoing orders: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Outgoing Order'],
    'description': 'Retrieve a specific outgoing order by ID (admin or customer who owns it).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Outgoing order retrieved successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Outgoing order not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_outgoing_order(id):
    """Get Single Outgoing Order"""
    try:
        user_id = CurrentUser.get_current_user_id()
        role = CurrentUser.get_role()

        result = OutgoingOrderService.get_outgoing_order_by_id(id, user_id, role)
        return success_response(200, "Outgoing order retrieved successfully", result)
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except ValueError as e:
        logger.warning(f"Value error: {str(e)}")
        return error_response(404, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error retrieving outgoing order ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Outgoing Order'],
    'description': 'Update an existing outgoing order (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'quantity_order': {'type': 'integer', 'example': 10},
                'discount': {'type': 'number', 'example': 10.0},
            }
        }}
    ],
    'responses': {
        200: {'description': 'Outgoing order updated successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input or insufficient stock', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Outgoing order not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_outgoing_order(id):
    """Update Outgoing Order"""
    try:
        role = CurrentUser.get_role()
        data = request.get_json()

        result = OutgoingOrderService.update_outgoing_order(id, data, role)
        return success_response(200, "Outgoing order updated successfully", result)
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
        logger.critical(f"Unexpected error updating outgoing order ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Outgoing Order'],
    'description': 'Delete an outgoing order (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Outgoing order deleted successfully',
              'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Outgoing order not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def delete_outgoing_order(id):
    """Delete Outgoing Order"""
    try:
        role = CurrentUser.get_role()

        OutgoingOrderService.delete_outgoing_order(id, role)
        return success_response(200, "Outgoing order deleted successfully", {})
    except PermissionError as e:
        logger.warning(f"Permission error: {str(e)}")
        return error_response(403, str(e))
    except ValueError as e:
        logger.warning(f"Value error: {str(e)}")
        return error_response(404, str(e))
    except Exception as e:
        logger.critical(f"Unexpected error deleting outgoing order ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")