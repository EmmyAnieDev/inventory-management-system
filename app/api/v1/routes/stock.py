from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from marshmallow import ValidationError
import logging

from app.api.utils.current_user import CurrentUser
from app.api.v1.schemas.stock import StockSchema
from app.api.utils.error_response import error_response
from app.api.utils.success_response import success_response
from app.api.v1.services.stock import StockService

logger = logging.getLogger(__name__)

bp = Blueprint("stock", __name__, url_prefix="/stocks")


@bp.route("/", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Stock'],
    'description': 'Retrieve all stock records (accessible to all authenticated users).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True}
    ],
    'responses': {
        200: {'description': 'Stocks retrieved successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_stocks():
    """Get All Stocks"""
    if not CurrentUser.check_role(['admin', 'customer', 'supplier']):
        logger.warning("Unauthorized attempt to access stocks")
        return error_response(403, "Access denied")

    try:
        stocks = StockService.get_all_stocks()
        logger.info(f"Retrieved {len(stocks)} stock records")
        return success_response(200, "Stocks retrieved successfully", stocks)
    except Exception as e:
        logger.critical(f"Unexpected error retrieving stocks: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Stock'],
    'description': 'Retrieve a specific stock record by ID (accessible to all authenticated users).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {'description': 'Stock retrieved successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        403: {'description': 'Access denied', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Stock not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def get_stock(id):
    """Get Single Stock"""
    if not CurrentUser.check_role(['admin', 'customer', 'supplier']):
        logger.warning(f"Unauthorized attempt to access stock ID: {id}")
        return error_response(403, "Access denied")

    try:
        stock = StockService.get_stock_by_id(id)

        if not stock:
            logger.warning(f"Stock ID {id} not found")
            return error_response(404, "Stock not found")

        logger.info(f"Stock retrieved: ID {id}")
        return success_response(200, "Stock retrieved successfully", stock)
    except Exception as e:
        logger.critical(f"Unexpected error retrieving stock ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")


@bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Stock'],
    'description': 'Update a stock record by ID (admin only).',
    'parameters': [
        {'name': 'Authorization', 'in': 'header', 'type': 'string', 'required': True},
        {'name': 'id', 'in': 'path', 'type': 'integer', 'required': True},
        {'name': 'body', 'in': 'body', 'required': True, 'schema': {
            'type': 'object',
            'properties': {
                'available_quantity': {'type': 'integer', 'example': 150},
                'product_price': {'type': 'number', 'example': 1099.99}
            }
        }}
    ],
    'responses': {
        200: {'description': 'Stock updated successfully', 'schema': {'$ref': '#/definitions/SuccessResponse'}},
        400: {'description': 'Invalid input', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        403: {'description': 'Admin access required', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        404: {'description': 'Stock not found', 'schema': {'$ref': '#/definitions/ErrorResponse'}},
        500: {'description': 'Server error', 'schema': {'$ref': '#/definitions/ErrorResponse'}}
    }
})
def update_stock(id):
    """Update a Stock"""
    if not CurrentUser.check_role(['admin']):
        logger.warning(f"Unauthorized attempt to update stock ID: {id}")
        return error_response(403, "Admin access required")

    try:
        data = request.get_json()
        schema = StockSchema(partial=True)
        validated_data = schema.load(data)
        logger.debug(f"Validated update data for stock ID {id}: {validated_data}")

        updated_stock = StockService.update_stock(id, validated_data)

        if not updated_stock:
            logger.warning(f"Stock ID {id} not found")
            return error_response(404, "Stock not found")

        logger.info(f"Stock updated: ID {id}")
        return success_response(200, "Stock updated successfully", updated_stock)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return error_response(400, f"Invalid input: {str(e)}")
    except Exception as e:
        logger.critical(f"Unexpected error updating stock ID {id}: {str(e)}")
        return error_response(500, "An unexpected error occurred")