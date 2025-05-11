from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.category import Category


class ProductSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "Product name is required."}
    )
    category_id = fields.Integer(
        required=True,
        error_messages={"required": "Category ID is required."}
    )
    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"required": "Quantity is required."}
    )
    price = fields.Float(
        required=True,
        validate=validate.Range(min=0),
        error_messages={"required": "Price is required."}
    )
    date_created = fields.DateTime(dump_only=True)

    @validates("category_id")
    def validate_category_id(self, value, **kwargs):
        if not Category.get_by_id(value):
            raise ValidationError("Category does not exist")