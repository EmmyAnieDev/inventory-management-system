from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.product import Product
from app.api.v1.models.supplier import Supplier


class IncomingOrderSchema(Schema):
    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(
        required=True,
        error_messages={"required": "Product ID is required."}
    )
    supplier_id = fields.Integer(
        required=True,
        error_messages={"required": "Supplier ID is required."}
    )
    quantity_supply = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={"required": "Quantity supply is required."}
    )
    total_price = fields.Float(dump_only=True)
    supply_date = fields.DateTime(dump_only=True)
    date_created = fields.DateTime(dump_only=True)

    @validates("product_id")
    def validate_product_id(self, value, **kwargs):
        if not Product.get_by_id(value):
            raise ValidationError("Product does not exist")

    @validates("supplier_id")
    def validate_supplier_id(self, value, **kwargs):
        if not Supplier.get_by_id(value):
            raise ValidationError("Supplier does not exist")