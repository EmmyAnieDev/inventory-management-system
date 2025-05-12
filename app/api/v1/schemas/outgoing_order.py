from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.product import Product
from app.api.v1.models.customer import Customer


class OutgoingOrderSchema(Schema):
    id = fields.Integer(dump_only=True)
    product_id = fields.Integer(
        required=True,
        error_messages={"required": "Product ID is required."}
    )
    customer_id = fields.Integer(
        required=True,
        error_messages={"required": "Customer ID is required."}
    )
    quantity_order = fields.Integer(
        required=True,
        validate=validate.Range(min=1),
        error_messages={"required": "Quantity order is required."}
    )
    total_price = fields.Float(dump_only=True)
    discount = fields.Float(
        required=False,
        validate=validate.Range(min=0, max=100),
        load_default=0.0,
        error_messages={"invalid": "Discount must be between 0 and 100."}
    )
    total_price_to_pay = fields.Float(dump_only=True)
    order_date = fields.DateTime(dump_only=True)
    date_created = fields.DateTime(dump_only=True)

    @validates("product_id")
    def validate_product_id(self, value, **kwargs):
        if not Product.get_by_id(value):
            raise ValidationError("Product does not exist")

    @validates("customer_id")
    def validate_customer_id(self, value, **kwargs):
        if not Customer.get_by_id(value):
            raise ValidationError("Customer does not exist")