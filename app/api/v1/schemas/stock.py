from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.product import Product


class StockSchema(Schema):
    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(
        required=True,
        error_messages={"required": "Product ID is required."}
    )
    available_quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"required": "Available quantity is required."}
    )
    product_price = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"required": "Product price is required."}
    )
    total_price = fields.Float(dump_only=True)
    date_created = fields.DateTime(dump_only=True)

    @validates("product_id")
    def validate_product_id(self, value, **kwargs):
        if not Product.get_by_id(value):
            raise ValidationError("Product does not exist")