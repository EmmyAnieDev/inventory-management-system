from marshmallow import Schema, fields, validate, validates, ValidationError
from app.api.v1.models.category import Category


class CategorySchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=50),
        error_messages={"required": "Category name is required."}
    )
    date_created = fields.DateTime(dump_only=True)

    @validates("name")
    def validate_name_unique(self, value, **kwargs):
        if Category.query.filter_by(name=value).first():
            raise ValidationError("Category name already exists")
